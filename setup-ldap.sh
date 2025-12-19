#!/bin/bash
# Setup script to populate LDAP with test users (6 profiles)

echo "Setting up LDAP with 6 test users..."

# Wait for LDAP to be ready
echo "Waiting for LDAP service to be fully ready..."
sleep 5

# Copy LDIF file to container
echo "Copying bootstrap LDIF to LDAP container..."
docker cp infra/ldap/bootstrap.ldif hr-ldap:/tmp/bootstrap.ldif

# Add users to LDAP
echo "Adding users to LDAP..."
docker exec hr-ldap ldapadd -x -H ldap://localhost -D "cn=admin,dc=safran,dc=local" -w "SecureAdminPass123!" -f /tmp/bootstrap.ldif 2>&1 | grep -v "Already exists" || true

echo "LDAP setup complete!"
echo ""
echo "Test users created (6 profiles):"
echo "  - alice / password (CADRE)"
echo "  - bob / password (CDI)"
echo "  - charlie / password (INTÉRIMAIRE)"
echo "  - david / password (STAGIAIRE)"
echo "  - emma / password (CDD)"
echo "  - frank / password (NON-CADRE)"
echo ""
echo "Application is ready at http://localhost:5173"
