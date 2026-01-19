# SysAid Authentication Notes

SysAid PDF export relies on an authenticated session.

- Authentication is performed outside this tooling
- A valid `JSESSIONID` cookie is required
- The cookie must be passed verbatim

No credential handling is implemented by design.
