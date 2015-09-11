/**
 * Created by phg49389 on 9/3/15.
 */

function submit(){
    var form = document.getElementById("classifieds");
    var array_of_results = [];
    var id, val;
    for(var i = 0; i < form.elements.length-1; i++){
        id = form.elements[i].id;
        if(id != "categories"){
            val = form.elements[i].value;
        }
        else{
            var selected = form.elements[i].selectedOptions;
            val = "";
            for(var j = 0; j < selected.length; j++){
                val += selected[j].value +";";
            }
        }
        array_of_results.push(id + "=" + val);
    }
    alert(array_of_results);
    $.ajax({
        type: "POST",
        url: "submitAd",
        //JSON.stringify(array_of_results)
        data: { data_pairs: "blah" }
    });//.done(function (response) {
        //alert(response);
        //var address = window.location.href;
        //var base = address.slice(0,address.indexOf("?")-1);
        //base += "/" + response;
        //window.location.href = base;
    //});
    alert("Past AJAX section");

}