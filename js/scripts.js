	function getRequest(){
		var xhr; 
    	try {  
    		xhr = new ActiveXObject('Msxml2.XMLHTTP');
    	}catch (e) {
        	try {   
        		xhr = new ActiveXObject('Microsoft.XMLHTTP');
        	}catch (e2) {
				try {  
					xhr = new XMLHttpRequest();
          		}catch (e3) {  xhr = false;   }
        	}
     	}
     	return xhr;
     	}

	function asyncEdit(cityID,action){
		var xhr =getRequest();
 		var elementID='item_'+cityID;
    	xhr.onreadystatechange  = function(test){ 
			if(xhr.readyState  == 4){
        		if(xhr.status  == 200) {
        			item = document.getElementById(elementID);
        			if(action=="enlever"){
        				document.getElementById("list_enlever").removeChild(item);
           				document.getElementById("list_ajouter").appendChild(item);
           				document.getElementById("action_"+cityID).value="ajouter";
          				document.getElementById("action_"+cityID).onclick = function(){asyncEdit(cityID,'ajouter')};
        			}
        			if(action=="ajouter"){
        				document.getElementById("list_ajouter").removeChild(item);
           				document.getElementById("list_enlever").appendChild(item);
           				document.getElementById("action_"+cityID).value="enlever";
        				document.getElementById("action_"+cityID).onclick = function(){asyncEdit(cityID,'enlever')};
         			}
        	    } else {
        	         document.getElementById('ajax').value="Error code " + xhr.status;
        	    }
        	 }
    	}; 

   		xhr.open("GET", "/manage?which_city="+cityID+"&action="+action,  true); 
   		xhr.send(null);
						
	}

	function asyncNewCity(){
		var http = getRequest();

		http.onreadystatechange  = function(){ 
			if(http.readyState  == 4){
        		if(http.status  == 200) {
     	         	/*document.getElementById('ajax').value=http.responseText;*/
     	         	node = document.createElement('li');
     	         	li = eval('(' + http.responseText + ')');
       				node.innerHTML = li.content;
       				node.id = li.id;
       				document.getElementById("list_enlever").appendChild(node);
        	    } else {
        	         document.getElementById('ajax').value="Error code " + http.status + " " +http.responseText;
        	    }
        	 }
    	};
		var test = document.getElementById("urlField").value;
 		var url="url="+test;
 		http.open("POST", "/me",  true); 
   		http.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
		http.setRequestHeader("Content-length", url.length);
		http.setRequestHeader("Connection", "close");
   		http.send(url);
   		document.getElementById("urlField").value=""
						
	}
