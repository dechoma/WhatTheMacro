Setup

- Configure environment variables (create `.env.local`):

```
VITE_API_URL=/api
# Dev convenience only; do not commit a real admin secret
# VITE_ADMIN_PASSWORD=dev-admin
```

- The Sign up form now requires an admin password, sent via `X-Admin-Password` header.


