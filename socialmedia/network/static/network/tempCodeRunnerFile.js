function editPostControl(postID) {
    let modal = document.getElementById("editpost{{post.id}}");
    var btn = document.getElementById("editbtn");
    var span = document.getElementsByClassName("close")[0];
    const postID=postID;
    btn.onclick = function() {
        modal.style.display = "block";
      }
    span.onclick = function() {
        modal.style.display = "none";
      }
      let saveButton = document.getElementsByClassName("modal-save");
      let modalBody = document.getElementsByClassName("form-control");

      // Get content of post to be edited
      let contentNode = document.getElementsByClassName("post-content");
      
      
      // Populate content with form to fill
      saveButton.onclick = function() {
        const submittedContent = modalBody.innerHTML;
        let csrftoken = getCookie('csrftoken');
        // Send PUT request
        fetch(`/post-comment/post`, {
            method: "PUT",
            body: JSON.stringify({
            id: postID,
            content: submittedContent,
            }),
            headers: {"X-CSRFToken": csrftoken}
        })
        .then((response) => {
            // if success - update post's content
            if (response.status === 201) {
                contentNode.innerHTML = submittedContent;
                console.log(`post id: ${postID} edited successfully`);
            }
            // if error - show alert and reload the page
            else {
                let response_body = await response.json();

                throw new Error(response_body.error);                        
            }
        })
        
    }
}
