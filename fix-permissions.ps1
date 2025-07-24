# Fix permissions for output directory
# Equivalent to chmod 777 output

Write-Host "Setting full permissions on output directory..."

# Method 1: Using icacls (Windows command)
icacls output /grant Everyone:(OI)(CI)F

# Method 2: Using PowerShell (alternative)
# $acl = Get-Acl output
# $accessRule = New-Object System.Security.AccessControl.FileSystemAccessRule("Everyone","FullControl","ContainerInherit,ObjectInherit","None","Allow")
# $acl.AddAccessRule($accessRule)
# Set-Acl output $acl

Write-Host "Permissions updated successfully!"
