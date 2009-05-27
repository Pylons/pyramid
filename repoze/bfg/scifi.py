# Tweak BFG slightly to allow for separate authentication and
# authorization policies, so we don't have security policies named
# e.g. "RepozeWhoInheritingACLSecurityPolicy".  We'll add
# IAuthenticationPolicy objects and IAuthorizationPolicy objects;
# these will be adapters.  We'll also change ISecurityPolicy to be an
# adapter rather than a utility.  We'll tweak the function API to use
# these adapters.

# b/w incompats: the "authorization" policy needs access to the
# context, which the APIs it maps to in a current BFG security policy
# don't have; code which depends on these APIs will need to change.

from zope.interface import implements
from zope.interface import Interface

class IAuthenticationPolicy(Interface):
    """ A multi-adapter on context and request """
    def authenticated_userid():
        """ Return the authenticated userid or None if no
        authenticated userid can be found """

    def effective_principals():
        """ Return a sequence representing the effective principals
        (including the userid and any groups belonged to by the
        current user, including 'system' groups such as Everyone and
        Authenticated"""

    def challenge():
        """ Return an IResponse object representing a challenge, such
        as a login form or a basic auth dialog """

    def remember(self, principal, token):
        """ Return a set of headers suitable for 'remembering' the
        principal on subsequent requests """
    
    def forget():
        """ Return a set of headers suitable for 'forgetting' the
        current user on subsequent requests"""

class IAuthorizationPolicy(Interface):
    """ An adapter on context """
    def permits(self, principals, permission):
        """ Return True if any of the principals is allowed the
        permission in the current context, else return False """
        
    def principals_allowed_by_permission(self, permission):
        """ Return a set of principal identifiers allowed by the permission """

class ISecurityPolicy(Interface):
    """ A multi-adapter on context and request """
    def permits(permission):
        """ Returns True if the combination of the authorization
        information in the context and the authentication data in
        the request allow the action implied by the permission """

    def authenticated_userid():
        """ Return the userid of the currently authenticated user or
        None if there is no currently authenticated user """

    def effective_principals():
        """ Return the list of 'effective' principals for the request.
        This must include the userid of the currently authenticated
        user if a user is currently authenticated."""

    def principals_allowed_by_permission(permission):
        """ Return a sequence of principal identifiers allowed by the
        ``permission`` in the model implied by ``context``.  This
        method may not be supported by a given security policy
        implementation, in which case, it should raise a
        ``NotImplementedError`` exception."""

    def forbidden():
        """ This method should return an IResponse object (an object
        with the attributes ``status``, ``headerlist``, and
        ``app_iter``) as a result of a view invocation denial.  The
        ``forbidden`` method of a security policy will be called by
        ``repoze.bfg`` when view invocation is denied (usually as a
        result of the ``permit`` method of the same security policy
        returning False to the Router).

        The ``forbidden`` method of a security will not be called when
        an ``IForbiddenResponseFactory`` utility is registered;
        instead the ``IForbiddenResponseFactory`` utility will serve
        the forbidden response.

        Note that the ``repoze.bfg.message`` key in the environ passed
        to the WSGI app will contain the 'raw' reason that view
        invocation was denied by repoze.bfg.  The ``context`` object
        passed in will be the context found by ``repoze.bfg`` when the
        denial was found and the ``request`` will be the request which
        caused the denial."""
    
# an implementation of an authentication policy that uses repoze.who

class RepozeWhoAuthenticationPolicy(object):
    """ A BFG authentication policy which obtains data from the
    repoze.who API """
    implements(IAuthenticationPolicy)
    def __init__(self, context, request):
        self.context = context
        self.request = request
        from repoze.who.api import api_from_environ
        self.api = api_from_environ(request.environ)

    def authenticated_userid(self):
        identity = self.api.authenticate()
        if identity is None:
            return None
        return identity['repoze.who.userid']

    def effective_principals(self):
        effective_principals = [Everyone]
        identity = self.api.authenticate()
        if identity is None:
            return effective_principals

        effective_principals.append(Authenticated)
        userid = identity['repoze.who.userid']
        groups = identity.get('groups', [])
        effective_principals.append(userid)
        effective_principals.extend(groups)

        return effective_principals

    def challenge(self):
        return self.api.challenge()

    def remember(self, principal, token):
        return self.api.remember({'repoze.who.userid':principal,
                                  'password':token})

    def forget(self):
        return self.api.forget()

# an implementation of an authentication policy that uses a cookie

class StandaloneAuthenticationPolicy:
    """ A BFG authentication policy which obtains data from a cookie
    and a local storage system """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def _check_password(self, userid, password):
        """ Return true if the password is good for the userid  """
        raise NotImplementedError # you get the idea

    def _groups_from_userid(self, userid):
        """ Return a sequence of groups given a user id """
        raise NotImplementedError # you get the idea

    def _userid_from_login(self, login):
        """ Return a userid given a login name """
        raise NotImplementedError # you get the idea

    def _decrypt(self, cookieval):
        """ Return decrypted login and password"""
        raise NotImplementedError # you get the idea

    def _encrypt(self, userid, password):
        """ Return encrypted hash of userid and password for cookie val """
        raise NotImplementedError # you get the idea

    def authenticated_userid(self):
        cookieval = request.cookies.get('oatmeal')
        try:
            login, password = self._decrypt(cookieval)
        except:
            return None
        userid = self._userid_from_login(login)
        if self._check_password(userid, password):
            return userid

    def effective_principals(self):
        effective_principals = [Everyone]
        userid = self.authenticated_userid()
        if userid is None:
            return effective_principals

        effective_principals.append(Authenticated)
        groups = self._groups_from_userid(userid)
        effective_principals.append(userid)
        effective_principals.extend(groups)

        return effective_principals
        
    def challenge(self):
        userid = self.authenticated_userid()
        if userid:
            return render_template_to_response('templates/forbidden.pt')
        else:
            return render_template_to_response('templates/login_form.pt')

    def remember(self, principal, token):
        cookieval = self._encrypt(principal, token)
        return [ ('Set-Cookie', 'oatmeal=%s' % cookieval) ]

    def forget(self):
        return [ ('Set-Cookie', 'oatmeal=') ]

# an implementation of an authorization policy that uses ACLs

class ACLAuthorizationPolicy(object):
    implements(IAuthorizationPolicy)
    def __init__(self, context):
        self.context = context
        
    def permits(self, principals, permission):
        """ """
        # do stuff to figure out of any of the principals is allowed
        # the permission by any ACL in the current context's hierarchy

    def principals_allowed_by_permission(self, permission):
        """ """
        # return the sequence of principals allowed by the permission
        # according to the ACLs in the current context' hierarchy

# present a rolled up "face" to both authn and autz policies in the
# form of a "security policy"; users will interact with this API
# rather than the authn or authz policies directly.

class SecurityPolicy(object):
    """ Use separate authn and authz to form a BFG security policy;
    this will never be overridden, it is concrete. It is an adapter. """
    implements(ISecurityPolicy)
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.authn = getMultiAdapter((self.context, self.request),
                                     IAuthenticationPolicy)
        self.authz = getAdapter(context, IAuthorizationPolicy)
        
    def permits(self, permission):
        principals = set(self.authn.effective_principals())

        if authz.permits(principals, permission):
            return True

        return False

    def authenticated_userid(self):
        return self.authn.authenticated_userid()

    def effective_principals(self):
        return self.authn.effective_principals()

    def principals_allowed_by_permission(self):
        return self.authz.principals_allowed_by_permission()

    def forbidden(self):
        return self.authn.challenge()

    def remember(self, principal, token):
        return self.authn.remember(principal, token)

    def forget(self):
        return self.authn.forget()
