window.onload = function () {
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
}

// Funciones de confirmar acciones
$(document).ready(function () {
    $("button#closeNoti").click(function () {
        $(this).closest(".error").addClass("hidden");
        $(this).closest(".info").addClass("hidden");
        $(this).closest(".warning").addClass("hidden");
        $(this).closest(".message").addClass("hidden");
    });
});

function Confirm_Delete_Funtion(){
    return confirm("¿Eliminar usuario?")
}

function Confirm_Update_Funtion(){
    return confirm("¿Actualizar datos del usuario?")
}