// $(document).ready(() => {
//     $('#slideshow .slick').slick({
//         autoplay: true,
//         autoplaySpeed: 500, // autoplaySpeed: 1000, or             autoplaySpeed: 2000,
//         dots: true,
//     });
// });
$(document).ready(() => {
    $('#slideshow .slick').slick({
        centerMode: true,
        centerPadding: '60px',
        slidesToShow: 3,
        autoplay: true,
        arrows:true,
        dots:true,
        autoplaySpeed: 1000,
        responsive: [
          {
            breakpoint: 768,
            settings: {
              arrows: false,
              centerMode: true,
              centerPadding: '40px',
              slidesToShow: 3
            }
          },
          {
            breakpoint: 480,
            settings: {
              arrows: false,
              centerMode: true,
              centerPadding: '40px',
              slidesToShow: 1
            }
          }
        ]
      })
});