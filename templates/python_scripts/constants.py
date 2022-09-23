DASHBOARDS_FIRST_PART = """<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GPW Analytics</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/shorthandcss@1.1.1/dist/shorthand.min.css" />
    <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Muli:200,300,400,500,600,700,800,900&display=swap" />
    <link rel="stylesheet" type="text/css"
        href="https://cdnjs.cloudflare.com/ajax/libs/slick-carousel/1.9.0/slick.min.css" />
    <link rel="stylesheet" type="text/css" href="//cdn.jsdelivr.net/npm/slick-carousel@1.8.1/slick/slick-theme.css" />
</head>

<body class="bg-black muli">
    <nav class="w-100pc flex flex-column md-flex-row md-px-10 py-5 bg-black">
        <div class="flex justify-between">
            <h5 class="red">Disclaimer: This is for testing purposes only</h5>
            <a data-toggle="toggle-nav" data-target="#nav-items" href="#"
                class="flex items-center ml-auto md-hidden indigo-lighter opacity-50 hover-opacity-100 ease-300 p-1 m-3">
                <i data-feather="menu"></i>
            </a>
        </div>
        <div id="nav-items" class="hidden flex sm-w-100pc flex-column md-flex md-flex-row md-justify-end items-center">
            <a href="/" class="button bg-white black fw-600 no-underline mx-5">Home</a>
            <a href="/db_choice" class="button bg-white black fw-600 no-underline mx-5">Connect with Database</a>
            <a href="/get_data" class="button bg-white black fw-600 no-underline mx-5">Download raw data</a>
        </div>
    </nav>

    <!-- hero section -->
    <section id="home" class="min-h-100vh flex justify-start items-center">
        <div>
            <div>
                <!-- <h1 class="white lh-2 md-lh-1 fw-900 ">Select company ticker, time period and download the data</h1> -->
            </div>
        </div>
        
        <div class="w-100pc md-w-50pc">
            <form action="show_dashboards" method="post">
            <h1 class="white lh-2 md-lh-1 fw-900 flex justify-center">Select Ticker, Period and Model</h1>
            <br>
            <hr>
            <div class="flex justify-center">
                <div class="w-30pc md-px-100 mb-100">
                    
                    <br>
                    <!-- <h2 class="white">Select company ticker and time period</h2> -->
                    <ul>
                        <br>
                        <li><p>.</p></li>
                        <hr>
                        <br>
                        <li class="my-3"><a class="white opacity-70 no-underline hover-underline">Ticker:</a></li>

                    </ul>
                </div>
                <div class="w-33pc md-px-10 mb-10">
                    <br>
                    
                        <ul>
                            <br>
                            <li><p>.</p></li>
                            <!-- <li><p class="white"><strong>General setup</strong></p></li> -->
                            <hr>
                            <br>
                            <li class="my-3"><select id="selectTickersPreds" name="tickerSelectionPreds"></select></li>


                        </ul>
                        <br>
                        <p>.</p>
                        <br>
                        <input class="btn btn-primary btn-xl" type="submit" Value="Show dashboard">
                </div>
            </div>
            <hr>
            <br>           
            </form>
        </div>
   
    </section>"""

DASHBOARDS_LAST_PART = """    </div>
    <script src="https://code.jquery.com/jquery-3.4.1.min.js"></script>
    <script src="https://unpkg.com/feather-icons"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/slick-carousel/1.9.0/slick.min.js"></script>
    <script src="https://cdn.jsdelivr.net/gh/cferdinandi/smooth-scroll@15.0.0/dist/smooth-scroll.polyfills.min.js"></script>
    <script src="static/scripts/script.js"></script>
    <script src="static/scripts/dropdown_dat_from.js"></script>
    <script src="static/scripts/dropdown_tickers_preds.js"></script>
    <script src="static/scripts/dropdown_models.js"></script>
</body>

</html>"""