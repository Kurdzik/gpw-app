DASHBOARDS_FIRST_PART = """<!DOCTYPE html>
<html lang="en" class="h-100">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>GPW Analytics</title>
    
    <link
      href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.1/dist/css/bootstrap.min.css"
      rel="stylesheet"
      integrity="sha384-iYQeCzEYFbKjA/T2uDLTpkwGzCiq6soy8tYaI1GyVh/UjpbCx/TYkiZhlZB6+fzT"
      crossorigin="anonymous"
    />
    <link rel="stylesheet" href="static/css/cover.css" />
    <link
      rel="stylesheet"
      href="https://fonts.googleapis.com/css?family=Muli:200,300,400,500,600,700,800,900&display=swap"
    />
  </head>

  <body class="d-flex h-100 text-center text-bg-dark">
    <div class="d-flex w-100 h-100 p-3 mx-auto flex-column">
      <header class="mb-auto">
        <nav
          class="navbar navbar-expand-lg navbar-dark nav-masthead justify-content-center"
        >
          <div class="container-fluid">
            <a class="text-white" href="#">
              <h3 class="float-md-start mb-0">GPW Analytics</h3>
            </a>
            <button
              class="navbar-toggler"
              type="button"
              data-bs-toggle="collapse"
              data-bs-target="#navbarSupportedContent"
              aria-controls="navbarSupportedContent"
              aria-expanded="false"
              aria-label="Toggle navigation"
            >
              <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarSupportedContent">
              <ul class="navbar-nav ms-auto mb-2 mb-lg-0">
                <li class="nav-item me-lg-4">
                  <a href="/" class="nav-link fw-bold py-1 px-0">Home</a>
                </li>
                <li class="nav-item me-lg-4">
                  <a href="/get_data" class="nav-link fw-bold py-1 px-0"
                    >Download raw data</a
                  >
                </li>
                <li class="nav-item me-lg-4">
                  <a href="/db_choice" class="nav-link fw-bold py-1 px-0"
                    >Connect with Database</a
                  >
                </li>
                <li class="nav-item">
                  <a href="/analytics" class="nav-link fw-bold py-1 px-0"
                    >Analytics</a
                  >
                </li>
              </ul>
            </div>
          </div>
        </nav>
      </header>
      <main class="px-3">
        <h1>Select which company you want to analyze</h1>
        <form
          action="show_dashboards"
          method="post"
          class="d-block my-5 get_data_form"
        >
          <div class="input-group mb-3 justify-content-center">
            <div class="input-group-prepend">
              <label class="input-group-text" for="selectTickersPreds"
                >Company:</label
              >
            </div>
            <select
              class="custom-select"
              id="selectTickersPreds"
              name="tickerSelectionPreds"
            ></select>
          </div>
          <input
            class="btn btn-success btn-lg mt-4 mx-auto d-block"
            type="submit"
            value="Show dashboards"
          />
        </form>
      </main>"""

DASHBOARDS_LAST_PART = """       <footer class="mt-auto text-white-50">
        <p>
          Created by
          <a href="https://github.com/Kurdzik" class="text-white">Kurdzik</a>
          and
          <a href="https://github.com/mikolajhere" class="text-white"
            >mikolajhere</a
          >
        </p>
      </footer>
    </div>

    <script
      src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.1/dist/js/bootstrap.bundle.min.js"
      integrity="sha384-u1OknCvxWvY5kfmNBILK2hRnQC3Pr17a+RTT6rIHI7NnikvbZlHgTPOOmMi466C8"
      crossorigin="anonymous"
    ></script>

    <script src="https://code.jquery.com/jquery-3.4.1.min.js"></script>
    <script src="https://unpkg.com/feather-icons"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/slick-carousel/1.9.0/slick.min.js"></script>
    <script src="https://cdn.jsdelivr.net/gh/cferdinandi/smooth-scroll@15.0.0/dist/smooth-scroll.polyfills.min.js"></script>
    <script src="static/scripts/script.js"></script>
    <script src="static/scripts/script.js"></script>
    <script src="static/scripts/dropdown_dat_from.js"></script>
    <script src="static/scripts/dropdown_tickers_preds.js"></script>
    <script src="static/scripts/dropdown_models.js"></script>
  </body>
</html>"""