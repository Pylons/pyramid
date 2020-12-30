import warnings
from zope.interface import implementer

from pyramid.config.actions import action_method
from pyramid.csrf import LegacySessionCSRFStoragePolicy
from pyramid.exceptions import ConfigurationError
from pyramid.interfaces import (
    PHASE1_CONFIG,
    PHASE2_CONFIG,
    IAuthenticationPolicy,
    IAuthorizationPolicy,
    ICSRFStoragePolicy,
    IDefaultCSRFOptions,
    IDefaultPermission,
    ISecurityPolicy,
)
from pyramid.security import LegacySecurityPolicy
from pyramid.util import as_sorted_tuple


class SecurityConfiguratorMixin:
    def add_default_security(self):
        self.set_csrf_storage_policy(LegacySessionCSRFStoragePolicy())

    @action_method
    def set_security_policy(self, policy):
        """Override the :app:`Pyramid` :term:`security policy` in the current
        configuration.  The ``policy`` argument must be an instance
        of a security policy or a :term:`dotted Python name`
        that points at an instance of a security policy.

        .. note::

           Using the ``security_policy`` argument to the
           :class:`pyramid.config.Configurator` constructor can be used to
           achieve the same purpose.

        """

        def register():
            self.registry.registerUtility(policy, ISecurityPolicy)

        policy = self.maybe_dotted(policy)
        intr = self.introspectable(
            'security policy',
            None,
            self.object_description(policy),
            'security policy',
        )
        intr['policy'] = policy
        self.action(
            ISecurityPolicy,
            register,
            order=PHASE2_CONFIG,
            introspectables=(intr,),
        )

    @action_method
    def set_authentication_policy(self, policy):
        """
        .. deprecated:: 2.0

            Authentication policies have been replaced by security policies.
            See :ref:`upgrading_auth_20` for more information.

        Override the :app:`Pyramid` :term:`authentication policy` in the
        current configuration.  The ``policy`` argument must be an instance
        of an authentication policy or a :term:`dotted Python name`
        that points at an instance of an authentication policy.

        .. note::

           Using the ``authentication_policy`` argument to the
           :class:`pyramid.config.Configurator` constructor can be used to
           achieve the same purpose.

        """
        warnings.warn(
            'Authentication and authorization policies have been deprecated '
            'in favor of security policies.  See "Upgrading '
            'Authentication/Authorization" in "What\'s New in Pyramid 2.0" '
            'of the documentation for more information.',
            DeprecationWarning,
            stacklevel=3,
        )

        def register():
            self.registry.registerUtility(policy, IAuthenticationPolicy)
            if self.registry.queryUtility(IAuthorizationPolicy) is None:
                raise ConfigurationError(
                    'Cannot configure an authentication policy without '
                    'also configuring an authorization policy '
                    '(use the set_authorization_policy method)'
                )
            if self.registry.queryUtility(ISecurityPolicy) is not None:
                raise ConfigurationError(
                    'Cannot configure an authentication and authorization'
                    'policy with a configured security policy.'
                )
            security_policy = LegacySecurityPolicy()
            self.registry.registerUtility(security_policy, ISecurityPolicy)

        policy = self.maybe_dotted(policy)
        intr = self.introspectable(
            'authentication policy',
            None,
            self.object_description(policy),
            'authentication policy',
        )
        intr['policy'] = policy
        # authentication policy used by view config (phase 3)
        self.action(
            IAuthenticationPolicy,
            register,
            order=PHASE2_CONFIG,
            introspectables=(intr,),
        )

    @action_method
    def set_authorization_policy(self, policy):
        """
        .. deprecated:: 2.0

            Authentication policies have been replaced by security policies.
            See :ref:`upgrading_auth_20` for more information.

        Override the :app:`Pyramid` :term:`authorization policy` in the
        current configuration.  The ``policy`` argument must be an instance
        of an authorization policy or a :term:`dotted Python name` that points
        at an instance of an authorization policy.

        .. note::

           Using the ``authorization_policy`` argument to the
           :class:`pyramid.config.Configurator` constructor can be used to
           achieve the same purpose.

        """
        warnings.warn(
            'Authentication and authorization policies have been deprecated '
            'in favor of security policies.  See "Upgrading '
            'Authentication/Authorization" in "What\'s New in Pyramid 2.0" '
            'of the documentation for more information.',
            DeprecationWarning,
            stacklevel=3,
        )

        def register():
            self.registry.registerUtility(policy, IAuthorizationPolicy)

        def ensure():
            if self.autocommit:
                return
            if self.registry.queryUtility(IAuthenticationPolicy) is None:
                raise ConfigurationError(
                    'Cannot configure an authorization policy without '
                    'also configuring an authentication policy '
                    '(use the set_authorization_policy method)'
                )

        policy = self.maybe_dotted(policy)
        intr = self.introspectable(
            'authorization policy',
            None,
            self.object_description(policy),
            'authorization policy',
        )
        intr['policy'] = policy
        # authorization policy used by view config (phase 3) and
        # authentication policy (phase 2)
        self.action(
            IAuthorizationPolicy,
            register,
            order=PHASE1_CONFIG,
            introspectables=(intr,),
        )
        self.action(None, ensure)

    @action_method
    def set_default_permission(self, permission):
        """
        Set the default permission to be used by all subsequent
        :term:`view configuration` registrations.  ``permission``
        should be a :term:`permission` string to be used as the
        default permission.  An example of a permission
        string:``'view'``.  Adding a default permission makes it
        unnecessary to protect each view configuration with an
        explicit permission, unless your application policy requires
        some exception for a particular view.

        If a default permission is *not* set, views represented by
        view configuration registrations which do not explicitly
        declare a permission will be executable by entirely anonymous
        users (any authorization policy is ignored).

        Later calls to this method override will conflict with earlier calls;
        there can be only one default permission active at a time within an
        application.

        .. warning::

          If a default permission is in effect, view configurations meant to
          create a truly anonymously accessible view (even :term:`exception
          view` views) *must* use the value of the permission importable as
          :data:`pyramid.security.NO_PERMISSION_REQUIRED`.  When this string
          is used as the ``permission`` for a view configuration, the default
          permission is ignored, and the view is registered, making it
          available to all callers regardless of their credentials.

        .. seealso::

            See also :ref:`setting_a_default_permission`.

        .. note::

           Using the ``default_permission`` argument to the
           :class:`pyramid.config.Configurator` constructor can be used to
           achieve the same purpose.
        """

        def register():
            self.registry.registerUtility(permission, IDefaultPermission)

        intr = self.introspectable(
            'default permission', None, permission, 'default permission'
        )
        intr['value'] = permission
        perm_intr = self.introspectable(
            'permissions', permission, permission, 'permission'
        )
        perm_intr['value'] = permission
        # default permission used during view registration (phase 3)
        self.action(
            IDefaultPermission,
            register,
            order=PHASE1_CONFIG,
            introspectables=(intr, perm_intr),
        )

    def add_permission(self, permission_name):
        """
        A configurator directive which registers a free-standing
        permission without associating it with a view callable.  This can be
        used so that the permission shows up in the introspectable data under
        the ``permissions`` category (permissions mentioned via ``add_view``
        already end up in there).  For example::

          config = Configurator()
          config.add_permission('view')
        """
        intr = self.introspectable(
            'permissions', permission_name, permission_name, 'permission'
        )
        intr['value'] = permission_name
        self.action(None, introspectables=(intr,))

    @action_method
    def set_default_csrf_options(
        self,
        require_csrf=True,
        token='csrf_token',
        header='X-CSRF-Token',
        safe_methods=('GET', 'HEAD', 'OPTIONS', 'TRACE'),
        check_origin=True,
        allow_no_origin=False,
        callback=None,
    ):
        """
        Set the default CSRF options used by subsequent view registrations.

        ``require_csrf`` controls whether CSRF checks will be automatically
        enabled on each view in the application. This value is used as the
        fallback when ``require_csrf`` is left at the default of ``None`` on
        :meth:`pyramid.config.Configurator.add_view`.

        ``token`` is the name of the CSRF token used in the body of the
        request, accessed via ``request.POST[token]``. Default: ``csrf_token``.

        ``header`` is the name of the header containing the CSRF token,
        accessed via ``request.headers[header]``. Default: ``X-CSRF-Token``.

        If ``token`` or ``header`` are set to ``None`` they will not be used
        for checking CSRF tokens.

        ``safe_methods`` is an iterable of HTTP methods which are expected to
        not contain side-effects as defined by RFC2616. Safe methods will
        never be automatically checked for CSRF tokens.
        Default: ``('GET', 'HEAD', 'OPTIONS', TRACE')``.

        ``check_origin`` is a boolean. If ``False``, the ``Origin`` and
        ``Referer`` headers will not be validated as part of automated
        CSRF checks.

        ``allow_no_origin`` is a boolean.  If ``True``, a request lacking both
        an ``Origin`` and ``Referer`` header will pass the CSRF check. This
        option has no effect if ``check_origin`` is ``False``.

        If ``callback`` is set, it must be a callable accepting ``(request)``
        and returning ``True`` if the request should be checked for a valid
        CSRF token. This callback allows an application to support
        alternate authentication methods that do not rely on cookies which
        are not subject to CSRF attacks. For example, if a request is
        authenticated using the ``Authorization`` header instead of a cookie,
        this may return ``False`` for that request so that clients do not
        need to send the ``X-CSRF-Token`` header. The callback is only tested
        for non-safe methods as defined by ``safe_methods``.

        .. versionadded:: 1.7

        .. versionchanged:: 1.8
           Added the ``callback`` option.

        .. versionchanged:: 2.0
           Added the ``allow_no_origin`` and ``check_origin`` options.

        """
        options = DefaultCSRFOptions(
            require_csrf=require_csrf,
            token=token,
            header=header,
            safe_methods=safe_methods,
            check_origin=check_origin,
            allow_no_origin=allow_no_origin,
            callback=callback,
        )

        def register():
            self.registry.registerUtility(options, IDefaultCSRFOptions)

        intr = self.introspectable(
            'default csrf view options',
            None,
            options,
            'default csrf view options',
        )
        intr['require_csrf'] = require_csrf
        intr['token'] = token
        intr['header'] = header
        intr['safe_methods'] = as_sorted_tuple(safe_methods)
        intr['check_origin'] = allow_no_origin
        intr['allow_no_origin'] = check_origin
        intr['callback'] = callback

        self.action(
            IDefaultCSRFOptions,
            register,
            order=PHASE1_CONFIG,
            introspectables=(intr,),
        )

    @action_method
    def set_csrf_storage_policy(self, policy):
        """
        Set the :term:`CSRF storage policy` used by subsequent view
        registrations.

        ``policy`` is a class that implements the
        :meth:`pyramid.interfaces.ICSRFStoragePolicy` interface and defines
        how to generate and persist CSRF tokens.

        """

        def register():
            self.registry.registerUtility(policy, ICSRFStoragePolicy)

        intr = self.introspectable(
            'csrf storage policy', None, policy, 'csrf storage policy'
        )
        intr['policy'] = policy
        self.action(ICSRFStoragePolicy, register, introspectables=(intr,))


@implementer(IDefaultCSRFOptions)
class DefaultCSRFOptions:
    def __init__(
        self,
        require_csrf,
        token,
        header,
        safe_methods,
        check_origin,
        allow_no_origin,
        callback,
    ):
        self.require_csrf = require_csrf
        self.token = token
        self.header = header
        self.safe_methods = frozenset(safe_methods)
        self.check_origin = check_origin
        self.allow_no_origin = allow_no_origin
        self.callback = callback
