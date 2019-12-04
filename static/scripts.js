document.addEventListener("init", function(event) {
  var page = event.target;
  if (page.id === "home") {
    // Update Age at diagnosis slider value live
    page.querySelector("#age-range").oninput = function() {
      var age_range = document.getElementById("age-range");
      document.getElementById("age-label").textContent =
        "Age at diagnosis (" + age_range.value + "):";
    };
    // Update tumour size slider value live
    page.querySelector("#tumour-size-range").oninput = function() {
      var tumour_size = document.getElementById("tumour-size-range");
      document.getElementById("tumour-size-label").textContent =
        "Tumour size (" + tumour_size.value + " mm):";
    };

    // Open menu
    page.querySelector("#menu-button-home").onclick = function() {
      document.querySelector("#myNavigator").pushPage("menu.html");
    };

    // Open help
    page.querySelector("#help-button-home").onclick = function() {
      document.querySelector("#myNavigator").pushPage("help.html");
    };

    // Enable Compute button when agreement checkbox is checked
    $("#agree-check").change(function() {
      if(this.checked) {
        $("#compute-button").prop('disabled', false);
      } else {
        $("#compute-button").prop('disabled', true);
      }
  });

    // When Compute button is tapped
    page.querySelector("#compute-button").onclick = function() {
      // Add spinner to Compute button
      $("#compute-button").toggleClass("compute-button-trans");
      $(".compute-label").toggleClass("compute-label-trans");
      $(".spinner").toggleClass("spinner-trans");

      // Count one submission with Google Analytics
      gtag("event", "submission");

      // Get selected options
      var age = Number(document.getElementById("age-range").value);
      var tumour_size = Number(
        document.getElementById("tumour-size-range").value
      );
      // Sex: 0=Male, 1=Female
      var sex = document.getElementById("sex-segment").getActiveButtonIndex();
      // Race: 0=White, 1=Black, 2=Other
      var race = document.getElementById("race-segment").getActiveButtonIndex();
      // Insurance: 0=Insured, 1=Uninsured, 2=Unknown
      var insurance = document
        .getElementById("insurance-segment")
        .getActiveButtonIndex();
      // Laterality: 0=Not bilateral, 1=Midline, 2=Bilateral
      var laterality = document
        .getElementById("laterality-segment")
        .getActiveButtonIndex();
      // Site: 0=Cerebral m, 1=Spinal m, 2=Other, 3=Meninges NOS
      var site = document.getElementById("site-select").selectedIndex;
      // Surgery switches ( | 0 for bool -> int)
      // [No sx, GTR, STR, Resection, Partial, Local, Radical, Other]
      var sx_array = [];
      for (i = 0; i < 8; i++) {
        sx_element_id = "sx-switch" + i;
        sx_array.push(document.getElementById(sx_element_id).checked | 0);
      }
      // Tumour behaviour: 0=Unknown, 1=Benign m, 2=Borderline malignancy, 3=Malignant
      var tumour_behaviour = document.getElementById("tumour-select")
        .selectedIndex;

      // Malignancy prediction
      var malignancy_features = ["/plot/malignancy", age, tumour_size];
      var malignancy_url = malignancy_features.join("/");
      $.ajax({
        url: malignancy_url,
        dataType: "html",
        type: "GET",
        success: function(data) {
          window.maligancy_data = data;
        }
      });

      // Survival prediction
      var survival_features = [
        "/plot/survival",
        age,
        tumour_size,
        sex,
        race,
        laterality,
        site,
        insurance,
        tumour_behaviour
      ];
      var survival_url = survival_features.concat(sx_array).join("/");
      $.ajax({
        url: survival_url,
        dataType: "html",
        type: "GET",
        success: function(data) {
          window.survival_data = data;
        }
      });
    };
  } else if (page.id === "results") {
    // Insert malignancy and survival result figures
    $("#malignancy-card").append(window.maligancy_data);
    $("#malignancy-card > svg").css({
      position: "relative",
      width: "100%",
      left: 0,
      top: 0
    });
    $("#malignancy-card > svg").removeAttr("height");
    $("#survival-card").append(window.survival_data);
    $("#survival-card > svg").css({
      position: "relative",
      width: "100%",
      left: 0,
      top: 0
    });
    $("#survival-card > svg").removeAttr("height");

    // Reset compute button (remove spinner)
    $("#compute-button").toggleClass("compute-button-trans");
    $(".compute-label").toggleClass("compute-label-trans");
    $(".spinner").toggleClass("spinner-trans");
  } else if (page.id === "menu") {
    page.querySelector("#paper-menuitem").onclick = function() {
      ons.notification.alert("This will link to the paper");
      // window.open('https://jeremymoreau.com/', '_blank');
    };
    var c_val = "ǈǄǌǉǑǊƟǏǀǗǀǈǜƋǈǊǗǀǄǐǥǈǄǌǉƋǈǆǂǌǉǉƋǆǄ";
    page.querySelector("#contact-menuitem").onclick = function() {
      window.open(deobfs(c_val), "_blank");
    };
    page.querySelector("#website-menuitem").onclick = function() {
      window.open("https://jeremymoreau.com/", "_blank");
    };
    // Open licence
    page.querySelector("#licence-menuitem").onclick = function() {
      document.querySelector("#myNavigator").pushPage("licence.html");
    };
  }
});

// Switch to results page once all Ajax requests are complete
$(document).ajaxStop(function() {
  document.querySelector("#myNavigator").pushPage("results.html");
});

function deobfs(str) {
  if (!str) str = "";
  str = str == "undefined" || str == "null" ? "" : str;
  try {
    var key = 421;
    var pos = 0;
    ostr = "";
    while (pos < str.length) {
      ostr = ostr + String.fromCharCode(key ^ str.charCodeAt(pos));
      pos += 1;
    }

    return ostr;
  } catch (ex) {
    return "";
  }
}
