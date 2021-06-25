function generarPassword(){
    var pass = '';
            var str = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' + 
                    'abcdefghijklmnopqrstuvwxyz0123456789@#$';
              
            for (i = 1; i <= 12; i++) {
                var char = Math.floor(Math.random() * str.length + 1);
                  
                pass += str.charAt(char)
            }
     document.getElementById("password").value=pass; 
    
        }