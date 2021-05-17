$(document).ready(function() {

    $("#form").validate({
      rules: {
        contraseña: {
          required:true,
          minlength: 8
        },
        nick: {
          required: true,
          minlength: 5
        },
      },
  
      messages : {
        contraseña: {
          minlength: "debe tener una mayuscula, una minuscula y almenos 8 caracteres"
        },
        nick: {
          minlength: "debe tener almenos 5 caracteres"
        },
      }
    });
  });