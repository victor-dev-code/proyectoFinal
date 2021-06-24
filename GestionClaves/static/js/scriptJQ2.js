$(document).ready(function() {

    $("#form").validate({
      rules: {
        contraseña: {
          required:true,
          minlength: 10
        },
        nick: {
          required: true,
          minlength: 5
        },
        token: {
          required: true,
          minlength: 7
        },
        nomCompleto : {
          required: true,
          minlength: 15
        },
        chat: {
          required: true,
          minlength: 9
        },
        tokt: {
          required: true,
          minlength: 46
        },
        email: {
          required: true,
          email: true
        },
        nomSitio: {
          required: true,
          minlength: 5
        },
        usuario: {
          required: true,
          minlength: 5
        },
        password: {
          required: true,
          minlength: 10
        },
        url: {
          required: true,
          minlength: 20
        },
        extra: {
          required: true,
          minlength: 10
        }
      },
  
      messages : {
        contraseña: {
          minlength: "debe tener una mayuscula, una minuscula y almenos 10 caracteres y un numero"
        },
        nick: {
          minlength: "debe tener almenos 5 caracteres"
        },
        token: {
          minlength: "debe tener almenos 7 caracteres"
        },
        nomCompleto : {
          minlength: "el nombre debe tener almenos 15 caracteres"
        },
        email: {
          email: "el correo debe estar en formato ejemplo@dominio.com"
        },
        chat: {
          minlength: "el chat id debe de tener 9 caracteres "
        },
        tokt: {
          minlength: "el token debe de tener 46 caracteres "
        },
        nomSitio: {
          minlength: "Escribe el nombre del sitio en el que usas la contraseña "
        },
        password: {
          minlength: "escribe la contraseña del sitio en el que la usas"
        },
        usuario: {
          minlength: "escribe el usuario del sitio en el que lo usas"
        },
        url: {
          minlength: "escribe la url del sitio a la que pertenece la cuenta"
        },
        extra: {
          minlength: "escribe aqui los detalles importantes de la cuenta"
        }
      }
    });
  });