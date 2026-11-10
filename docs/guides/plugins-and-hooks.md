# Plugins and hooks

Hooks: `before_stage`, `after_stage`, `on_error`, `on_complete`.

```python
container.hooks.add("after_stage", lambda stage, ctx, status: print(stage.name, status))
```

Hook exceptions are captured in `hooks.failures` and reported by `/readyz`.
