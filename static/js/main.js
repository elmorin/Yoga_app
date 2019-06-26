$(document).ready(function () {
    // Init
    $('.image-section').hide();
    $('.loader').hide();
    $('#result').hide();

    // Upload Preview
    function readURL(input) {
        if (input.files && input.files[0]) {
            var reader = new FileReader();
            reader.onload = function (e) {
                $('#imagePreview').css('background-image', 'url(' + e.target.result + ')');
                $('#imagePreview').hide();
                $('#imagePreview').fadeIn(650);
                console.log(e.target.input.files[0].name);

            }
            reader.readAsDataURL(input.files[0]);
        }
    }
    
    function readVideo(input) {
		if (input.files && input.files[0]) {
    		var reader = new FileReader();
    		reader.onload = function(e) {
        		$('.myvideo').attr('src', e.target.result);
    		};
    	reader.readAsDataURL(input.files[0]);
        }
    }

    $("#imageUpload").change(function () {
        $('.image-section').show();
        $('#btn-predict').show();
        $('#result').text('');
        $('#result').hide();
        readURL(this);
    });
    $(function() {
    $('.upload-video-file').on('change', function(){
      if (isVideo($(this).val())){
        $('.video-preview').attr('src', URL.createObjectURL(this.files[0]));
        $('.video-prev').show();
      }
      else
      {
        $('.upload-video-file').val('');
        $('.video-prev').hide();
        alert("Only video files are allowed to upload.")
      }
    });
});

// If user tries to upload videos other than these extension , it will throw error.
function isVideo(filename) {
    var ext = getExtension(filename);
    switch (ext.toLowerCase()) {
    case 'm4v':
    case 'avi':
    case 'mpg':
    case 'mp4':
    case 'mov':
    case 'mpg':
    case 'mpeg':
        // etc
        return true;
    }
    return false;
}

function getExtension(filename) {
    var parts = filename.split('.');
    return parts[parts.length - 1];
}
    
    
    
    
    
    
    
    
    
    

    // Predict
    $('#btn-predict').click(function () {
        var form_data = new FormData($('#upload-file')[0]);

        // Show loading animation
        $(this).hide();
        $('.loader').show();

        // Make prediction by calling api /predict
        $.ajax({
            type: 'POST',
            url: '/predict',
            data: form_data,
            contentType: false,
            cache: false,
            processData: false,
            async: true,
            success: function (data) {
                // Get and display the result
                $('.loader').hide();
                $('#result').fadeIn(600);
                $('#result').text(' Prediction:  ' + data);
                console.log('Success!');
            },
        });
    });

});
