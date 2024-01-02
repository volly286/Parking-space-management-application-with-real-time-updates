function reserveSpot(spotId) {
            window.location.href = '/reserve/' + spotId;
        }

        function releaseSpot() {
            const decision = confirm("Doriți să eliberați locul de parcare rezervat?");
            if (decision) {
                window.location.href = '/release';
            }
        }
        function hideFlashMessages() {
            var messages = document.querySelectorAll('.flash-message');
            messages.forEach(function(message) {
                setTimeout(function() {
                    message.style.display = 'none';
                }, 3000); // 
            });
        }

        window.onload = function() {
            hideFlashMessages();
        };
 var socket = io.connect('https://271c-95-76-207-177.ngrok-free.app/');

        socket.on('update_parking_spot', function(data) {
            var spotElement = document.getElementById("spot-" + data.spot_id);
            if (spotElement) {
                var statusText = 'Locul ' + data.spot_id;
                if (data.status === 'reserved') {
                    spotElement.classList.add('reserved');
                    spotElement.removeAttribute('onclick');
                    statusText += ' (Rezervat de ' + data.license_number + ')';
                } else {
                    spotElement.classList.remove('reserved');
                    spotElement.setAttribute('onclick', 'reserveSpot("' + data.spot_id + '")');
                    statusText += ' (Disponibil)';
                }
                spotElement.textContent = statusText;
            }
        });

        socket.on('spot_released', function(data) {
        var spotElement = document.getElementById("spot-" + data.spot_id);
        if (spotElement) {
            var statusText = 'Locul ' + data.spot_id + ' (Disponibil)';
            spotElement.classList.remove('reserved');
            spotElement.setAttribute('onclick', 'reserveSpot("' + data.spot_id + '")');
            spotElement.textContent = statusText;
        }
    });
