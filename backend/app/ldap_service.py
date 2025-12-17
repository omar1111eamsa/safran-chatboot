"""
LDAP service for user authentication and profile retrieval.
"""

import logging
from typing import Optional, Dict
from ldap3 import Server, Connection, ALL, SUBTREE
from ldap3.core.exceptions import LDAPException, LDAPBindError

from .config import settings

logger = logging.getLogger(__name__)


class LDAPService:
    """Service for LDAP operations."""
    
    def __init__(self):
        """Initialize LDAP server connection."""
        self.server = Server(
            settings.ldap_server_uri,
            get_info=ALL,
            connect_timeout=5
        )
        self.base_dn = settings.ldap_base_dn
    
    def authenticate_user(self, username: str, password: str) -> bool:
        """
        Authenticate user against LDAP.
        
        Args:
            username: LDAP username (uid)
            password: User password
            
        Returns:
            True if authentication successful, False otherwise
        """
        user_dn = f"uid={username},ou=People,{self.base_dn}"
        
        try:
            conn = Connection(
                self.server,
                user=user_dn,
                password=password,
                auto_bind=True
            )
            conn.unbind()
            logger.info(f"User {username} authenticated successfully")
            return True
            
        except LDAPBindError as e:
            logger.warning(f"Authentication failed for user {username}: {str(e)}")
            return False
            
        except LDAPException as e:
            logger.error(f"LDAP error during authentication for {username}: {str(e)}")
            return False
    
    def get_user_profile(self, username: str) -> Optional[Dict[str, str]]:
        """
        Retrieve user profile from LDAP.
        
        Args:
            username: LDAP username (uid)
            
        Returns:
            Dictionary with user profile data or None if not found
        """
        try:
            # Bind with admin credentials to search
            conn = Connection(
                self.server,
                user=settings.ldap_admin_dn,
                password=settings.ldap_admin_password,
                auto_bind=True
            )
            
            # Search for user
            search_filter = f"(uid={username})"
            conn.search(
                search_base=f"ou=People,{self.base_dn}",
                search_filter=search_filter,
                search_scope=SUBTREE,
                attributes=['cn', 'mail', 'employeeType', 'departmentNumber']
            )
            
            if not conn.entries:
                logger.warning(f"User {username} not found in LDAP")
                conn.unbind()
                return None
            
            entry = conn.entries[0]
            
            profile = {
                'username': username,
                'full_name': str(entry.cn.value) if entry.cn else username,
                'email': str(entry.mail.value) if entry.mail else f"{username}@serini.local",
                'employee_type': str(entry.employeeType.value) if entry.employeeType else 'Unknown',
                'department': str(entry.departmentNumber.value) if entry.departmentNumber else 'General'
            }
            
            conn.unbind()
            logger.info(f"Retrieved profile for user {username}")
            return profile
            
        except LDAPException as e:
            logger.error(f"LDAP error retrieving profile for {username}: {str(e)}")
            return None


# Global LDAP service instance
ldap_service = LDAPService()
