// document.addEventListener('DOMContentLoaded', function () {
//     // Dummy data for demonstration
//     var labels = ['Label 1', 'Label 2', 'Label 3', 'Label 4', 'Label 5'];
//     var data1 = [10, 25, 15, 30, 20];
//     var data2 = [5, 15, 10, 20, 25];

//     var ctx1 = document.getElementById('chart1').getContext('2d');
//     var chart1 = new Chart(ctx1, {
//         type: 'line',
//         data: {
//             labels: labels,
//             datasets: [{
//                 label: 'Chart 1',
//                 data: data1,
//                 borderColor: 'rgba(75, 192, 192, 1)',
//                 borderWidth: 2,
//                 fill: false
//             }]
//         },
//         options: {
//             responsive: true,
//             maintainAspectRatio: false,
//             scales: {
//                 x: {
//                     type: 'category',
//                     labels: labels
//                 },
//                 y: {
//                     beginAtZero: true
//                 }
//             }
//         }
//     });

//     var ctx2 = document.getElementById('chart2').getContext('2d');
//     var chart2 = new Chart(ctx2, {
//         type: 'bar',
//         data: {
//             labels: labels,
//             datasets: [{
//                 label: 'Chart 2',
//                 data: data1,
//                 backgroundColor: 'rgba(255, 99, 132, 0.5)',
//                 borderColor: 'rgba(255, 99, 132, 1)',
//                 borderWidth: 1
//             }]
//         },
//         options: {
//             responsive: true,
//             maintainAspectRatio: false,
//             scales: {
//                 x: {
//                     type: 'category',
//                     labels: labels
//                 },
//                 y: {
//                     beginAtZero: true
//                 }
//             }
//         }
//     });

//     var ctx3 = document.getElementById('chart3').getContext('2d');
//     var chart3 = new Chart(ctx3, {
//         type: 'line',
//         data: {
//             labels: labels,
//             datasets: [{
//                 label: 'Chart 3',
//                 data: data2,
//                 borderColor: 'rgba(255, 206, 86, 1)',
//                 borderWidth: 2,
//                 fill: false
//             }]
//         },
//         options: {
//             responsive: true,
//             maintainAspectRatio: false,
//             scales: {
//                 x: {
//                     type: 'category',
//                     labels: labels
//                 },
//                 y: {
//                     beginAtZero: true
//                 }
//             }
//         }
//     });

//     var ctx4 = document.getElementById('chart4').getContext('2d');
//     var chart4 = new Chart(ctx4, {
//         type: 'bar',
//         data: {
//             labels: labels,
//             datasets: [{
//                 label: 'Chart 4',
//                 data: data2,
//                 backgroundColor: 'rgba(54, 162, 235, 0.5)',
//                 borderColor: 'rgba(54, 162, 235, 1)',
//                 borderWidth: 1
//             }]
//         },
//         options: {
//             responsive: true,
//             maintainAspectRatio: false,
//             scales: {
//                 x: {
//                     type: 'category',
//                     labels: labels
//                 },
//                 y: {
//                     beginAtZero: true
//                 }
//             }
//         }
//     });
// });
