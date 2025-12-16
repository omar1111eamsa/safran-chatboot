#!/bin/bash
# Setup script to populate LDAP with test users

echo "🔧 Setting up LDAP with test users..."

# Wait for LDAP to be ready
echo "Waiting for LDAP service to be fully ready..."
sleep 5

# Copy LDIF file to container
echo "Copying bootstrap LDIF to LDAP container..."
docker cp infra/ldap/bootstrap.ldif hr-ldap:/tmp/bootstrap.ldif

# Add users to LDAP
echo "Adding users to LDAP..."
docker exec hr-ldap ldapadd -x -H ldap://localhost -D "cn=admin,dc=serini,dc=local" -w "SecureAdminPass123!" -f /tmp/bootstrap.ldif 2>&1 | grep -v "Already exists" || true

echo "✅ LDAP setup complete!"
echo ""
echo "Test users created:"
echo "  - alice / password (CDI - Cadre)"
echo "  - bob / password (CDD - Non-Cadre)"
echo "  - charlie / password (Intérim)"
echo "  - david / password (Stagiaire)"
echo ""
echo "🚀 Application is ready at http://localhost:5173"
