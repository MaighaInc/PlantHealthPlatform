# Security

> Authentication, authorization, and safe operation for Plant Health System

## Considerations

- Authentication and authorization (PHP-27)
- API input validation
- Secrets management — never in repo
- CORS configuration
- Database credential protection
- Unsafe file/image uploads
- Command injection prevention
- Arbitrary model loading restrictions
- Malicious image processing limits
- **Actuator authorization** — GPIO/irrigation control

## Critical Rule

Never expose GPIO or irrigation control without proper authorization in production.

Manual irrigation flow:

```text
authorization → safety validation → relay ON → event logged → max duration → relay OFF
```

## ML Security

- Validate model paths and versions
- Reject untrusted model files in production
- Low-confidence predictions → UNKNOWN, not forced actuation

## Related Docs

- [../design/IRRIGATION_SAFETY.md](../design/IRRIGATION_SAFETY.md)
- [../design/API.md](../design/API.md)
- [../plans/ROADMAP.md](../plans/ROADMAP.md) — PHP-27
