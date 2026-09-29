# SprinHub

Aplicación para la centralización de información de clientes y sus respectivos proyectos y/o recursos.

## Diseño de la BDD

El diseño de la base de de datos está pensado para ser sencillo y mantenible en el tiempo. A continuación el diagrama
con la estructura de la base de datos:

```mermaid

erDiagram
	clientes ||--o{ proyectos : references
	entornos }o--|| proyectos : references
	repositorios }o--|| proyectos : references
	servicios }o--|| proyectos : references
	proyectos ||--o{ dominios : references
	documentacion_enlaces }o--|| proyectos : references
	comandos }o--|| proyectos : references
	notas }o--|| proyectos : references

	clientes {
		INTEGER id
		VARCHAR(255) nombre
		VARCHAR(255) CIF
		VARCHAR(255) telefono
	}

	proyectos {
		INTEGER id
		INTEGER id_cliente
		VARCHAR(255) nombre
		TEXT(65535) descripcion
	}

	entornos {
		INTEGER id
		INTEGER id_proyecto
		TIPO__ENTORNO tipo
		VARCHAR(255) url
	}

	repositorios {
		INTEGER id
		INTEGER id_proyecto
		TIPO__REPOSITORIO tipo
		VARCHAR(255) url
	}

	servicios {
		INTEGER id
		INTEGER id_proyecto
		VARCHAR(255) nombre
	}

	dominios {
		INTEGER id
		INTEGER id_proyecto
		VARCHAR(255) url
	}

	documentacion_enlaces {
		INTEGER id
		INTEGER id_proyecto
		VARCHAR(255) titulo
		VARCHAR(255) url
	}

	comandos {
		INTEGER id
		INTEGER id_proyecto
		VARCHAR(255) nombre
		TEXT(65535) instruccion
	}

	notas {
		INTEGER id
		INTEGER id_proyecto
		VARCHAR(255) descripcion
		TEXT(65535) contenido
	}

