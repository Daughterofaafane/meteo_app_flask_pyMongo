$(document).ready(function () {
    $('#scroll').DataTable({
      "scrollY": "50vh",
      "scrollCollapse": true,
    });
    $('.dataTables_length').addClass('bs-select');
  });