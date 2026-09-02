# Checklist de seguridad antes de publicar

- [ ] Ejecutar `PREPARE_GITHUB.bat`.
- [ ] Revisar `git status` antes del primer commit.
- [ ] Confirmar que `.env*` reales están ignorados.
- [ ] Confirmar que `.terraform/` y `*.tfstate*` están ignorados.
- [ ] Buscar `AKIA`, `ASIA`, `BEGIN PRIVATE KEY`, `ghp_`, `github_pat_`, `sk-`.
- [ ] Revisar YAML de Secrets para asegurar que son placeholders/demo o generados en runtime.
- [ ] No subir `kubeconfig`.
- [ ] No subir archivos de certificados privados.
- [ ] No incluir bases SQLite/locales con datos personales.
- [ ] No incluir capturas con información real.
- [ ] No reutilizar `Admin123!` en ningún despliegue real.
- [ ] Elegir conscientemente una licencia antes de aceptar contribuciones.
