# KNOWME-Proyecto_Realidad_Aumentada
Proyecto de realidad aumentada realizada en Python para la asignatura 'Computación Ubicua e Inteligencia Ambiental' de la Universidad de Granada.

**Nota de conexión**: Para el correcto funcionamiento de la aplicación es necesario estar conectado a la red de la UGR, ya sea con 'eduroam' o mediante la VPN. Esto es debido a que la base de datos se encuentra almacenada en la misma.

La aplicación consiste en una red social, con creación de cuenta e inicio de sesión al abrirla.

### Realidad Aumentada
Al iniciar sesión, se muestra la cámara del dispositivo, y se escanean los rostros que aparezcan en ella. Al escanear una cara, si dicha persona tiene cuenta registrada, etiqueta su nombre en lo alto, si esa persona es conocida para el usuario actual, es decir, se ha añadido como amigo a algún grupo, la etiqueta con un color determinado asociado al grupo correspondiente, si es desconocido, lo muestra en gris. 
Por ejemplo: amigos - verde, compañeros de clase - azul, desconocido - gris. 

Cada usuario tiene una información a mostrar según se quiera, como la edad, el teléfono, o el nombre de usuario de otras redes sociales. Esta información ampliada solo se muestra mediante un menú desplegable si nos encontramos muy cerca de la misma, si está alejado, únicamente se muestra el nombre de usuario.

Tras identificarnos, la pantalla muestra varios menús:

### Botón Amigos
Lista los amigos asociados a la cuenta actual. Estos se pueden clasificar por grupos, cada grupo tendrá un color asignado para identificarlos rapidamente al ser escaneados. Por ejemplo: amigos - verde, compañeros de clase - azul.

### Botón Añadir_Amigo
Muestra un menú de búsqueda de usuarios.

### Botón Perfil
Permite editar la información del usuario actual.

## Botón micrófono
Activa el micrófono para usar la aplicación mediante comandos de voz
Comandos de voz válidos en la aplicacion:

- "abrir amigos" / "amigos" -> Abre el menu Amigos

- "abrir perfil" / "perfil" / "editar perfil" -> Abre el menu Perfil

- "añadir amigo" / "nuevo amigo" / "añadir amigos" -> Abre el menu Añadir amigos

- "añadir grupo" / "nuevo grupo" / "añadir grupos" -> Abre el menu Nuevo grupo

- "salir" / "volver" / "menu principal" / "menu inicio" / "inicio" -> Vuelve al menu de Inicio de Sesión
