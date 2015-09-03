/**
 * Created by phg49389 on 9/3/15.
 */

function submit(){
    var form = document.getElementById("classifieds");
    var array_of_results = [];
    var id, val;
    for(var i = 0; i < form.elements.length; i++){
        id = form.elements[i].id;
        alert("id is " + id);
        if(id != "categories"){
            val = form.elements[i].value;
        }
        else{
            val = form.elements[i].selectedOptions;
        }
        alert(val);
        //array_of_results.push(id + "=" + val);
    }
    //$.ajax({
    //    type: "POST",
    //    url: "submit",
    //    data: { data_pairs: JSON.stringify(array_of_results) }
    //});//.done(function (response) {
        //var address = window.location.href;
        //var base = address.slice(0,address.indexOf("?")-1);
        //base += "/" + response;
        //window.location.href = base;
    //});

}