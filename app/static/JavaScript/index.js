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

$(document).ready(function () {
    $("button#closeNoti").click(function () {
        $(this).closest(".error").addClass("hidden");
        $(this).closest(".info").addClass("hidden");
        $(this).closest(".warning").addClass("hidden");
        $(this).closest(".message").addClass("hidden");
    });
});