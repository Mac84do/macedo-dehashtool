#!/usr/bin/env python3
"""
Unit tests for extraction engine with diverse field sets and nested JSON.
"""

import unittest
from unittest.mock import patch
import pandas as pd
from result_extraction_v2 import (
    extract_all_fields, 
    _sanitize_column_names,
    _detect_hash_columns, 
    list_hash_columns,
    _intelligent_cleanup
)

class TestExtractionEngine(unittest.TestCase):
    """Test extraction engine with mocked responses containing diverse field sets."""
    
    def test_basic_field_extraction(self):
        """Test basic field extraction with simple nested data."""
        mock_response = {
            'entries': [
                {
                    'email': 'user@example.com',
                    'password': 'hash1',
                    'nested': {
                        'field': 'nested_value'
                    }
                }
            ]
        }

        df = extract_all_fields(mock_response)
        
        # Verify basic structure
        self.assertEqual(len(df), 1)
        self.assertIn('email', df.columns)
        self.assertIn('password', df.columns)
        self.assertIn('nested_field', df.columns)
        
        # Verify data
        self.assertEqual(df.iloc[0]['email'], 'user@example.com')
        self.assertEqual(df.iloc[0]['password'], 'hash1')
        self.assertEqual(df.iloc[0]['nested_field'], 'nested_value')
    
    def test_diverse_field_sets(self):
        """Test extraction with diverse field sets across entries."""
        mock_response = {
            'entries': [
                {
                    'id': '1',
                    'email': 'user1@example.com',
                    'password': 'pass123',
                    'username': 'user1',
                    'domain': 'example.com',
                    'md5_hash': '5d41402abc4b2a76b9719d911017c592'
                },
                {
                    'id': '2',
                    'email': 'user2@test.org',
                    'password': 'secret456',
                    'phone': '+1-555-0123',
                    'address': {'street': '123 Main St', 'city': 'Anytown'},
                    'sha256_hash': 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f'
                },
                {
                    'id': '3',
                    'email': 'admin@company.net',
                    'username': 'admin',
                    'name': 'System Administrator',
                    'bcrypt_hash': '$2a$10$N9qo8uLOickgx2ZMRZoMye',
                    'user_profile': {
                        'last_login': '2023-01-15',
                        'settings': {
                            'theme': 'dark',
                            'notifications': True
                        }
                    }
                }
            ]
        }
        
        df = extract_all_fields(mock_response)
        
        # Verify all entries are present
        self.assertEqual(len(df), 3)
        
        # Verify diverse fields are captured
        expected_columns = [
            'id', 'email', 'password', 'username', 'domain', 'name', 'phone', 'address',
            'md5_hash', 'sha256_hash', 'bcrypt_hash', 'address_street', 'address_city',
            'user_profile_last_login', 'user_profile_settings_theme', 'user_profile_settings_notifications'
        ]
        
        for col in expected_columns:
            self.assertIn(col, df.columns, f"Column {col} should be present")
        
        # Verify nested data is properly flattened
        self.assertEqual(df.iloc[1]['address_street'], '123 Main St')
        self.assertEqual(df.iloc[1]['address_city'], 'Anytown')
        self.assertEqual(df.iloc[2]['user_profile_last_login'], '2023-01-15')
        self.assertEqual(df.iloc[2]['user_profile_settings_theme'], 'dark')
        self.assertTrue(df.iloc[2]['user_profile_settings_notifications'])
    
    def test_column_sanitization(self):
        """Test column name sanitization."""
        test_df = pd.DataFrame({
            'user.profile.name': ['John Doe'],
            'address info': ['123 Main St'],
            'email__address': ['test@example.com'],
            'UPPER_CASE': ['value']
        })
        
        sanitized_df = _sanitize_column_names(test_df)
        
        expected_columns = ['user_profile_name', 'address_info', 'email_address', 'upper_case']
        self.assertListEqual(list(sanitized_df.columns), expected_columns)
    
    def test_hash_column_detection(self):
        """Test detection of hash columns by name and content."""
        test_df = pd.DataFrame({
            'email': ['user@example.com', 'admin@test.com'],
            'md5_hash': ['5d41402abc4b2a76b9719d911017c592', '098f6bcd4621d373cade4e832627b4f6'],
            'sha256_password': ['ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'a665a45920422f9d417e4867efde4f28e04afe7a6b1a24ebf4ff8f6a7d34e12f'],
            'bcrypt_field': ['$2a$10$N9qo8uLOickgx2ZMRZoMye', '$2a$10$abcdefghijklmnopqrstuv'],
            'regular_field': ['value1', 'value2'],
            'hex_looking': ['deadbeefcafebabe1234567890abcdef', 'feedfacedeadbeef0123456789abcdef']  # 32 char hex
        })
        
        hash_columns = _detect_hash_columns(test_df)
        
        # Should detect hash columns by name
        self.assertIn('md5_hash', hash_columns)
        self.assertIn('sha256_password', hash_columns)
        self.assertIn('bcrypt_field', hash_columns)
        
        # Should detect hex patterns
        self.assertIn('hex_looking', hash_columns)
        
        # Should not detect regular fields
        self.assertNotIn('email', hash_columns)
        self.assertNotIn('regular_field', hash_columns)
    
    def test_intelligent_cleanup(self):
        """Test intelligent cleanup of duplicates and empty rows."""
        test_df = pd.DataFrame({
            'email': ['user1@example.com', 'user2@example.com', 'user1@example.com', None, ''],
            'password': ['pass123', 'pass456', 'pass123', 'orphaned', None]
        })
        
        cleaned_df = _intelligent_cleanup(test_df)
        
        # Should remove exact duplicates and completely empty rows
        self.assertEqual(len(cleaned_df), 4)  # Original had 5, should be 4 after cleanup (only exact duplicate removed)
        
        # Should have reset index
        self.assertListEqual(list(cleaned_df.index), [0, 1, 2, 3])
    
    def test_empty_response_handling(self):
        """Test handling of empty API responses."""
        empty_response = {'entries': []}
        df = extract_all_fields(empty_response)
        
        self.assertTrue(df.empty)
        self.assertEqual(len(df), 0)
    
    def test_missing_entries_key(self):
        """Test error handling when entries key is missing."""
        invalid_response = {'success': True, 'total': 0}
        
        with self.assertRaises(KeyError) as context:
            extract_all_fields(invalid_response)
        
        self.assertIn("'entries' key not found", str(context.exception))
    
    def test_invalid_entries_type(self):
        """Test error handling when entries is not a list."""
        invalid_response = {'entries': 'not_a_list'}
        
        with self.assertRaises(ValueError) as context:
            extract_all_fields(invalid_response)
        
        self.assertIn("'entries' must be a list", str(context.exception))
    
    def test_deeply_nested_json(self):
        """Test extraction of deeply nested JSON structures."""
        mock_response = {
            'entries': [
                {
                    'id': '1',
                    'email': 'user@example.com',
                    'metadata': {
                        'source': {
                            'breach': {
                                'name': 'Example Breach',
                                'date': '2023-01-15',
                                'details': {
                                    'records': 1000000,
                                    'verified': True
                                }
                            }
                        }
                    }
                }
            ]
        }
        
        df = extract_all_fields(mock_response)
        
        # Verify deeply nested fields are flattened
        self.assertIn('metadata_source_breach_name', df.columns)
        self.assertIn('metadata_source_breach_date', df.columns)
        self.assertIn('metadata_source_breach_details_records', df.columns)
        self.assertIn('metadata_source_breach_details_verified', df.columns)
        
        # Verify data
        self.assertEqual(df.iloc[0]['metadata_source_breach_name'], 'Example Breach')
        self.assertEqual(df.iloc[0]['metadata_source_breach_details_records'], 1000000)
        self.assertTrue(df.iloc[0]['metadata_source_breach_details_verified'])
    
    def test_list_hash_columns_function(self):
        """Test the exported list_hash_columns function."""
        mock_response = {
            'entries': [
                {
                    'email': 'user@example.com',
                    'md5_hash': '5d41402abc4b2a76b9719d911017c592',
                    'sha256_hash': 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f'
                }
            ]
        }
        
        df = extract_all_fields(mock_response)
        
        # Mock console output to avoid printing during tests
        with patch('result_extraction_v2.Console'):
            hash_cols = list_hash_columns(df)
        
        self.assertIn('md5_hash', hash_cols)
        self.assertIn('sha256_hash', hash_cols)
        self.assertNotIn('email', hash_cols)

if __name__ == '__main__':
    unittest.main()

