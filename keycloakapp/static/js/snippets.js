/**** Tools *****/
function isEmail(email) {
  var regex = /^([a-zA-Z0-9_.+-])+\@(([a-zA-Z0-9-])+\.)+([a-zA-Z0-9]{2,4})+$/;
  return regex.test(email);
}

function isDate(dateStr) {
  var regex = /^(\d{1,2})(\/|-)(\d{1,2})(\/|-)(\d{4})$/;
  return regex.test(dateStr);  
}
/******************/

function removeGroup(clickedElement) {
  const group = clickedElement.getAttribute('data-group-id')
  const user = clickedElement.getAttribute('data-user-id')

  $.ajax({
    type: 'POST',
    url: "/api-removegroup",
    data: JSON.stringify({'group': group, 'user': user}),
    contentType: 'application/json',
    success: function(data){
      location.reload()
    }
  })
}

function addGroup(clickedElement) {
  const group = clickedElement.getAttribute('data-group-id')
  const user = clickedElement.getAttribute('data-user-id')

  $.ajax({
    type: 'POST',
    url: "/api-addgroup",
    data: JSON.stringify({'group': group, 'user': user}),
    contentType: 'application/json',
    success: function(data){
      location.reload()
    }
  })
}

function generateSerialNumber() {

  $.ajax({
    type: 'GET',
    url: "/api-getlastserial",
    contentType: 'application/json',
    success: function(data){
      var date = new Date()
      serialNumber = Number(data.slice(0, 4)) + 1
      const month = ("0" + (date.getMonth() + 1)).slice(-2)
      serialNumber += date.getFullYear().toString() + month.toString()
      $("#modal-id").removeClass('spinner-border')
      $("#modal-id").val(serialNumber)
      console.log(serialNumber)
    }
  })
}

async function modifyCoCoop(number, value) {
  await $.ajax({
    type: 'GET',
    url: "/api-getuserbynumber?number=" + number,
    contentType: 'application/json',
    success: function(data){
      if( data != 'error' ){
        for ( const prop in data['attributes'] ) {
          var attribute = data['attributes'][`${prop}`][0]
          
          if( prop == "co-coop" ) {
            data['attributes'][`${prop}`][0] = value
          }
        }

        const payload = { 'firstName': data['firstName'], 'lastName': data['lastName'], 'email': data['email'], 'attributes': data['attributes'] }
        const datas = { 'id': data['id'], 'payload': payload }

        $.ajax({
          type: 'POST',
          url: "/api-modifyuser",
          data: JSON.stringify(datas),
          contentType: 'application/json',
          success: function(data){
          }
        })
      }
    }
  })
}

async function user() {
  var sendRequest = true

  $("#modal-spinner").show()

  var action = $("#action").text()
  var id = $("#user-id").text()
  var firstName = $("#modal-firstName").val()
  firstName = firstName.substring(0, 1).toUpperCase() + firstName.substring(1)
  
  var lastName = $("#modal-lastName").val()
  lastName = lastName.substring(0, 1).toUpperCase() + lastName.substring(1)
  
  var profession = $("#modal-profession").val()
  profession = profession.substring(0, 1).toUpperCase() + profession.substring(1)

  var city = $("#modal-city").val()
  city = city.substring(0, 1).toUpperCase() + city.substring(1)

  /** Check format of email address **/
  if( isEmail($("#modal-email").val()) ){
    var email = $("#modal-email").val()
    $("#modal-email").removeClass('is-invalid')
  } else {
    sendRequest = false
    $("#modal-email").addClass('is-invalid')
  }
  
  /** Check format of birthday date **/
  if( $("#modal-birthday").val() == "" || isDate($("#modal-birthday").val()) ) {
    var birthday = $("#modal-birthday").val()
    $("#modal-birthday").removeClass('is-invalid')
  } else {
    sendRequest = false
    $("#modal-birthday").addClass('is-invalid')
  }

  if( $("#modal-co-coop").val() != "" ) {
    cocoop = $("#modal-co-coop").val().split(' - ')[1]
  } else {
    cocoop = ""
  }

  const attributes = { 
                      'id': [$("#modal-id").val()],
                      'adresse.adresse': [$("#modal-adress").val()], 
                      'adresse.complement': [$("#modal-adress-add").val()], 
                      'adresse.code_postal': [$("#modal-postalZip").val()], 
                      'adresse.ville': [city], 
                      'fullName': [firstName + " " + lastName], 
                      'telephone': [$("#modal-phone").val()], 
                      'date_naissance': [birthday],
                      'profession': [profession],
                      'conjoint': [$("#modal-spouse").val()],
                      'co-coop': [cocoop],
                      'genre': [$("#modal-gender").val()], 
                      'statut': [$("#modal-status").val()], 
                      'locale': 'fr'
                    }

  if( action == "new" ) {
    const datas = { 'firstName': firstName, 'lastName': lastName, 'email': email, 'attributes': attributes }
    
    await modifyCoCoop(cocoop, $("#modal-id").val())
    
    if( sendRequest ){
      $.ajax({
        type: 'POST',
        url: "/api-newuser",
        data: JSON.stringify(datas),
        contentType: 'application/json',
        success: function(data){
          if( data['message'] != 'error' ){
            window.location.replace("/users/?lastName="+lastName+"&firstName="+firstName+"&appId=")
          } else {
            console.log(data['content'].split(':')[2].split('}')[0])
          }
        }
      })
    }
  } else {
    const payload = { 'firstName': firstName, 'lastName': lastName, 'email': email, 'attributes': attributes }
    const datas = { 'id': id, 'payload': payload }
    const oldcocoop = $("#co-coop-modify").text()

    if( oldcocoop != "" ) {
      await modifyCoCoop(oldcocoop, "")
    }
    await modifyCoCoop(cocoop, $("#modal-id").val())

    $.ajax({
      type: 'POST',
      url: "/api-modifyuser",
      data: JSON.stringify(datas),
      contentType: 'application/json',
      success: function(data){
        if( data != 'error' ){
          window.location.replace("/users/?lastName="+lastName+"&firstName="+firstName+"&appId=")
        }
      }
    })
  }
}

function activation() {
  var id = $("#user-id").text()
  var activation = $("#activation").text()
  var firstName = $("#firstName").val()
  var lastName = $("#lastName").val()
  const datas = { "activation": activation, "id": id }

  $.ajax({
    type: 'POST',
    url: "/api-activation",
    data: JSON.stringify(datas),
    contentType: 'application/json',
    success: function(data){
      if( data['message'] != 'error' ){
        $("#modal-spinner").hide()
        window.location.replace("/users/?lastName="+lastName+"&firstName="+firstName+"&appId=")
      } else {
        console.log(data['content'].split(':')[2].split('}')[0])
      }
    }
  })
}

/***************************************************************************************/
/*** J'efface les 3 champs de recherche et je referme les listes dépliées ***/
/***************************************************************************************/
function erase(){
  $("#firstName").val("")
  $("#lastName").val("")
  $("#appId").val("")
  $(".list").each(function(index) {
      $(this).hide()
  })
}

/***************************************************************************************/
/*** J'efface toutes les listes de groupes et je n'affiche que celle qui est dépliée ***/
/***************************************************************************************/
$(document).ready(function(){
  let deployed = $.cookie('deployed')

  $(".list").hide()
  $(".list").each(function(index) {
    if( this.id == deployed ){
      $(this).show()
    }
  })
  $("#modal-spinner").hide()
  $("#modal-co-coop").autocomplete({ source: '../api-getusers?req=' + $("#modal-co-coop").val() })

  $("#userModal").on("show.bs.modal", function(event) {
    // Get the button that triggered the modal
    var button = $(event.relatedTarget)

    // Extract value from the custom data-* attribute
    var action = button.data("action")
    var title = button.data("title")
    var value = button.data("value").replace(/True/g, '"True"').replace(/False/g, '"False"')
    value = value.replace(/{'/g, '{"')
    value = value.replace(/'}/g, '"}')
    value = value.replace(/\['/g, '["')
    value = value.replace(/']/g, '"]')
    value = value.replace(/':/g, '":')
    value = value.replace(/ '/g, ' "')
    value = value.replace(/',/g, '",')

    $(".modal-title").text(title)
    if( action == "new" ){
      $(".modal-header").removeClass("header-primary")
      $(".modal-header").addClass("header-success")
      $("#modal-id").addClass("spinner-border")
    } else {
      $(".modal-header").removeClass("header-success")
      $(".modal-header").addClass("header-primary")
    }
    
    $('#action').html(action)

    if( value != "") {
      var user = JSON.parse(value)
      $("#co-coop-modify").html(user['user']['attributes']['co-coop'][0].split(' - ')[1])

      $('#user-id').html(user['user']['id'])
      $("#modal-lastName").val(user['user']['lastName'])
      $("#modal-firstName").val(user['user']['firstName'])
      $("#modal-email").val(user['user']['email'])
      $("#modal-id").val(user['user']['attributes']['id'])
      $("#modal-adress").val(user['user']['attributes']['adresse.adresse'])
      $("#modal-adress-add").val(user['user']['attributes']['adresse.complement'])
      $("#modal-postalZip").val(user['user']['attributes']['adresse.code_postal'])
      $("#modal-city").val(user['user']['attributes']['adresse.ville'])
      $("#modal-phone").val(user['user']['attributes']['telephone'])
      $("#modal-birthday").val(user['user']['attributes']['date_naissance'])
      $("#modal-profession").val(user['user']['attributes']['profession'])
      $("#modal-spouse").val(user['user']['attributes']['conjoint'])
      $("#modal-co-coop").val(user['user']['attributes']['co-coop'])
      $("#modal-gender").val(user['user']['attributes']['genre'])
      $("#modal-status").val(user['user']['attributes']['statut'])
    } else {
      generateSerialNumber()
    }
  })
})

$("#userModal").on("hide.bs.modal", function(event) {
  $('#action').text("")
  $('#user-id').text("")
  $("#co-coop-modify").text("")
  $("#modal-lastName").val("")
  $("#modal-firstName").val("")
  $("#modal-email").val("")
  $("#modal-id").val("")
  $("#modal-adress").val("")
  $("#modal-adress-add").val("")
  $("#modal-postalZip").val("")
  $("#modal-city").val("")
  $("#modal-phone").val("")
  $("#modal-birthday").val("")
  $("#modal-profession").val("")
  $("#modal-spouse").val("")
  $("#modal-co-coop").val("")
  $("#modal-gender").val("")
  $("#modal-status").val("")
})

$("#activationUserModal").on("show.bs.modal", function(event) {
  var button = $(event.relatedTarget)
  var id = button.data("id")
  var fullName = button.data("fullname")
  fullName = fullName.replace(/\['/g, '')
  fullName = fullName.replace(/']/g, '')
  var activation = button.data("activation")

  $('#user-id').html(id)
  $('#activation').html(activation)
  $("#modal-user-fullname").html(fullName)

  if( activation == "disable" ) {
    $("#modal-user-header").html("Désactivation d'un coopérateur")
    $(".modal-header").removeClass("header-success")
    $(".modal-header").addClass("bg-danger")
    $(".modal-header").addClass("text-white")
  } else {
    $("#modal-user-header").html("Activation d'un coopérateur")
    $(".modal-header").removeClass("bg-danger")
    $(".modal-header").removeClass("text-white")
    $(".modal-header").addClass("header-success")
  }
})

$("#userModal").on("hide.bs.modal", function(event) {
  $('#user-id').text("")
  $("#modal-user-fullname").html("")
})

$(".name").click( function(){
  if( $(this).next().is(":hidden") ){
    $(this).next().show()
    $.cookie('deployed', $(this).next().attr('id'))
  }
  else {
    $(this).next().hide()
    $.cookie('deployed', null)
  }
})

function logout(){
  $.cookie('deployed', null)
  window.location.replace("/logout")
}