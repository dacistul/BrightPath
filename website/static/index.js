function cancelAppointment(appointmentId) {
    fetch('/cancel-appointment', {
        method: "POST",
        body: JSON.stringify({ appointmentId: appointmentId }),
    }).then((_res) => {
        window.location.href = "/";
    });
}

function cancelReservation(reservationId) {
    fetch('/cancel-reservation', {
        method: "POST",
        body: JSON.stringify({ reservationId: reservationId }),
    }).then((_res) => {
        window.location.href = "/";
    });
}