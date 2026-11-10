{{- define "app.name" -}}{{ .Chart.Name }}{{- end -}}
{{- define "app.labels" -}}app.kubernetes.io/name: {{ include "app.name" . }}{{- end -}}
