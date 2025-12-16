#!/bin/bash
# Script to add users to LDAP after it starts

set -e

LDAP_HOST="${LDAP_HOST:-ldap-service}"
LDAP_PORT="${LDAP_PORT:-389}"
LDAP_BASE_DN="${LDAP_BASE_DN:-dc=serini,dc=local}"
LDAP_ADMIN_DN="${LDAP_ADMIN_DN:-cn=admin,dc=serini,dc=local}"
LDAP_ADMIN_PASSWORD="${LDAP_ADMIN_PASSWORD:-SecureAdminPass123!}"

echo "Waiting for LDAP to be ready..."
sleep 10

echo "Adding organizational units and users..."

# Create LDIF content
cat > /tmp/bootstrap.ldif << 'EOF'
dn: ou=People,dc=serini,dc=local
objectClass: organizationalUnit
ou: People

dn: ou=Groups,dc=serini,dc=local
objectClass: organizationalUnit
ou: Groups

dn: uid=alice,ou=People,dc=serini,dc=local
objectClass: inetOrgPerson
objectClass: organizationalPerson
objectClass: person
objectClass: top
cn: Alice Dupont
sn: Dupont
givenName: Alice
uid: alice
mail: alice.dupont@serini.local
employeeType: CDI
title: Cadre
departmentNumber: IT
userPassword: password

dn: uid=bob,ou=People,dc=serini,dc=local
objectClass: inetOrgPerson
objectClass: organizationalPerson
objectClass: person
objectClass: top
cn: Bob Martin
sn: Martin
givenName: Bob
uid: bob
mail: bob.martin@serini.local
employeeType: CDD
title: Non-Cadre
departmentNumber: Sales
userPassword: password

dn: uid=charlie,ou=People,dc=serini,dc=local
objectClass: inetOrgPerson
objectClass: organizationalPerson
objectClass: person
objectClass: top
cn: Charlie Bernard
sn: Bernard
givenName: Charlie
uid: charlie
mail: charlie.bernard@serini.local
employeeType: Intérim
title: Non-Cadre
departmentNumber: Logistics
userPassword: password

dn: uid=david,ou=People,dc=serini,dc=local
objectClass: inetOrgPerson
objectClass: organizationalPerson
objectClass: person
objectClass: top
cn: David Petit
sn: Petit
givenName: David
uid: david
mail: david.petit@serini.local
employeeType: Stagiaire
title: Non-Cadre
departmentNumber: Marketing
userPassword: password

dn: cn=employees,ou=Groups,dc=serini,dc=local
objectClass: groupOfNames
cn: employees
member: uid=alice,ou=People,dc=serini,dc=local
member: uid=bob,ou=People,dc=serini,dc=local
member: uid=charlie,ou=People,dc=serini,dc=local
member: uid=david,ou=People,dc=serini,dc=local

dn: cn=cadres,ou=Groups,dc=serini,dc=local
objectClass: groupOfNames
cn: cadres
member: uid=alice,ou=People,dc=serini,dc=local
EOF

# Add entries to LDAP
ldapadd -x -H ldap://${LDAP_HOST}:${LDAP_PORT} -D "${LDAP_ADMIN_DN}" -w "${LDAP_ADMIN_PASSWORD}" -f /tmp/bootstrap.ldif

echo "LDAP bootstrap completed successfully!"
