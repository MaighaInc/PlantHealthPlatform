# Versioned model artifacts (PHP-11+)

Filenames must include semantic version, e.g.:

```text
plant-health-classifier-1.0.0.joblib
plant-health-classifier-1.0.0.meta.json
plant-health-mlp-1.0.0.pt
plant-health-mlp-1.0.0.onnx
registry.json
```

Never use ambiguous names like `final_final_v2.pt`.

See [ADR-0002](../../docs/architecture/adr/0002-classical-before-feature-mlp-onnx.md): classical RF is the tabular baseline; MLP+ONNX is the Stage-4 edge export path.
