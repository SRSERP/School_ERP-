;(function($) {
    "use strict";
    
    $('ul.dropdown-menu [data-toggle=dropdown]').on('click', function(event) {
        event.preventDefault(); 
        event.stopPropagation(); 
        $(this).parent().siblings().removeClass('open');
        $(this).parent().toggleClass('open');
    });


    //$(document).ready(function(){
    //    $("nav.navbar-default").sticky({topSpacing:0})
    //})

    

    
    function offcanvasActivator(){
        if ( $('.offcanvas-toggler').length ){
            $('.offcanvas-toggler').on('click', function(){
                $('.offcanvas-menu,.offcanvas_closer').toggleClass('open')
            });
            $('.offcanvas_closer,.close-offcanvas').on('click',function(){
                $('.offcanvas-menu,.offcanvas_closer').removeClass('open')
            })
        }
    }
    offcanvasActivator();
    
    function countDownActive(){
        if ( $('#comingsoon-countdown').length ){
             $('#comingsoon-countdown').countdown('2018/10/05', function(event) { 
                 $(this).html(event.strftime(
                     '<div class="days"><span class="number">%-D</span><span class="string">%!D:Day,Days;</span></div>'+
                     '<div class="hours"><span class="number">%H</span><span class="string">%!H:Hour,Hours;</span></div>'+
                     '<div class="minutes"><span class="number">%M</span><span class="string">%!M:Minute,Minutes;</span></div>'+
                     '<div class="seconds"><span class="number">%S</span><span class="string">%!S:Second,Seconds;</span></div>'
                ))
            })
        }
    }
    countDownActive();
    
    
    
    function navbarAffix(){
        if ( $('.navbar').length ){
            var affixTop =  $('.navbar').offset().top;
            $('.navbar').affix({
                offset: {
                    top: affixTop,
                    bottom: function () {
                        return (this.bottom = $('.footer').outerHeight(false))
                    }
                }
            })
        }
    }
//    navbarAffix();
    
    
    
    $(function () {
      $('[data-toggle="tooltip"]').tooltip()
    })
    
    $(document).ready(function(){
        
        
    });
    
    $(window).load(function(){
        
        
        
        
    })
    /*work Image Popup*/
    function imagePopup(){
        if ($('.test-popup-link').length) {            
            $('.test-popup-link').magnificPopup({
                type: 'image'
            })
        }
    }    
    imagePopup();
    
    /*Project Filter 2*/
    function workIsotopeFilter(){
        if( $('#portfolio').length ){
            $('#portfolio').imagesLoaded(function(){
                $('#portfolio').isotope({
                    itemSelector: '.simpleportfolio-columns-3',
                    layoutMode: 'fitRows'                    
                })
            });

            $('#portfolio-filter li').on( 'click', function() {
                $('#portfolio-filter').find('.active').removeClass('active');
                $(this).addClass('active');
                var $filterValue = $(this).data('filter');
                $('#portfolio').isotope({ filter: $filterValue })
            })
        }
    }
    workIsotopeFilter();

    
//    progress-bar....//
    
    $(".progress-element").each(function() {
        $(this).waypoint(function() {
            var progressBar = $(".progress-bar");
            progressBar.each(function(indx){
                $(this).css("width", $(this).attr("aria-valuenow") + "%")
            })
        }, {
            triggerOnce: true,
            offset: 'bottom-in-view'

        });
    });
/*... circle-progress-bar=====*/
    
    $(".pie-chart").each(function() {
        $(this).waypoint(function() {
            $('.pie-chart').circleProgress({
                startAngle:-1.6,
                size: 150,
                thickness:2,
                duration: 2000,
                easing: "circleProgressEase",
                emptyFill: 'transparent',
                fill: {
                    color: ["#1193d4"]
                }
            });
          }, {
              triggerOnce: true,
              offset: 'bottom-in-view'

            });
        });
    
    function circle_progress(){
        if( $('.circle').length ){
            $(".circle").each(function() {
                $(this).waypoint(function() {
                    $('.circle').circleProgress({
                        startAngle:-1.6,
                        size: 150,
                        duration: 2000,
                        easing: "circleProgressEase",
                        emptyFill: '#fafafa',
                        lineCap: 'round'
                    })
                }, {
                    triggerOnce: true,
                    offset: 'bottom-in-view'
                })
            })
        }
    }
    
    function counterActivator(){
        if ( $('.counter').length ){
            $('.counter').counterUp({
                delay: 70,
                time: 1000
            })
        }
    }
    counterActivator();
    
    function revolutionSliderActiver () {
        if ($('.slidercontainer #rev_slider').length ) {
            $("#rev_slider").revolution({
                sliderType:"standard",
                sliderLayout:"auto",
                
                delay:9000,
                startwidth:1170,
                startheight:550,
                startWithSlide:0,

                fullScreenAlignForce:"off",
                autoHeight:"off",
                minHeight:"off",

                shuffle:"off",

                onHoverStop:"on",

                thumbWidth:100,
                thumbHeight:50,
                thumbAmount:3,

                hideThumbsOnMobile:"off",
                hideNavDelayOnMobile:1500,
                hideBulletsOnMobile:"off",
                hideArrowsOnMobile:"on",
                hideThumbsUnderResoluition:0,

                hideThumbs:0,
                hideTimerBar:"off",

                keyboardNavigation:"on",

                navigationType:"none",
                navigationArrows:"solo",
                navigationStyle:"preview1",

                navigationHAlign:"center",
                navigationVAlign:"bottom",
                navigationHOffset:30,
                navigationVOffset:30,

                soloArrowLeftHalign:"left",
                soloArrowLeftValign:"center",
                soloArrowLeftHOffset:20,
                soloArrowLeftVOffset:0,

                soloArrowRightHalign:"right",
                soloArrowRightValign:"center",
                soloArrowRightHOffset:20,
                soloArrowRightVOffset:0,

                touchenabled:"on",
                swipe_velocity:"0.7",
                swipe_max_touches:"1",
                swipe_min_touches:"1",
                drag_block_vertical:"false",

                parallax:"mouse",
                parallaxBgFreeze:"on",
                parallaxLevels:[10,7,4,3,2,5,4,3,2,1],
                parallaxDisableOnMobile:"off",

                stopAtSlide:-1,
                stopAfterLoops:-1,
                hideCaptionAtLimit:0,
                hideAllCaptionAtLilmit:0,
                hideSliderAtLimit:0,

                dottedOverlay:"none",

                spinned:"spinner4",

                fullWidth:"off",
                forceFullWidth:"off",
                fullScreen:"off",
                fullScreenOffsetContainer:"#topheader-to-offset",
                fullScreenOffset:"0px",

                panZoomDisableOnMobile:"off",

                simplifyAll:"on",

                shadow:0
            })
        }
    }
    revolutionSliderActiver ();
    
    
    function revSliderActivator() {
        if ( $('.banner').length ){
            $('.banner').revolution({
                
            })
        }
    }
    
    
    /*----------------------------------------------------*/
    /*  Google Map
    /*----------------------------------------------------*/        
    function mapBox () {
        if ( $( '#mapBox' ).length ){
            var $lat = $('#mapBox').data('lat');
            var $lon = $('#mapBox').data('lon');
            var $zoom = $('#mapBox').data('zoom');
            
            var map = new GMaps({
                el: '#mapBox',
                lat: $lat,
                lng: $lon,
                scrollwheel: false,
                scaleControl: true,
                streetViewControl: true,
                panControl: true,
                disableDoubleClickZoom: true,
                mapTypeControl: true,
                zoom: $zoom
            }) 
        }
    }
    mapBox();
    
    $(window).ready(function(){
        circle_progress();
    })
    
})(jQuery)