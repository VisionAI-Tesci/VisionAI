$(document).ready(function() {
    //alert("Cargado")
    $('#Hamster-loader').fadeOut();
    $('body').removeClass('hidden');
    $('.container_Father').removeClass('hidden');
    $('.section-camera-container').removeClass('hidden');
    $('.Copyright').removeClass('hidden');
    $('.conteiner-header-page').removeClass('hidden');
    $('.container-section-help').removeClass('hidden');
    $('.container-user-registrer').removeClass('hidden');
    $('.container-user').removeClass('hidden');
    $('body').css("overflow","visible");
});

// Funciones de confirmar acciones
$(document).ready(function() {
    $("button#closeNoti").click(function () {
        $(this).closest(".error").addClass("hidden");
        $(this).closest(".info").addClass("hidden");
        $(this).closest(".warning").addClass("hidden");
        $(this).closest(".message").addClass("hidden");
    });
});

function Confirm_Delete_Funtion(){
    return confirm("¿Eliminar usuario?");
}

function Confirm_Update_Funtion(){
    return confirm("¿Actualizar datos del usuario?");
}

function Confirm_LogOut_Funtion(){
    return confirm("¿Cerrar sesión?");
}

function Confirm_UpPasword_Funtion(){
    return confirm("¿Actualizar contraseña?");
}
function Confirm_UpImg_Funtion(){
    return confirm("Este proceso puede tardar, NO ACTUALICE/CAMBIE LA PÁGINA. ¿Continuar el proceso?");
}
function Open_New_Window(){
    window.open("/Seccion_Fotos","_blank", "left = 500,menubar=0,location=yes,resizable=0,scrollbars=0,status=1,titlebar=0,width=670,height=500");
}