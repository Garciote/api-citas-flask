{
  description = "Flask API Citas - DEV";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = {
    self,
    nixpkgs,
    flake-utils,
  }:
    flake-utils.lib.eachDefaultSystem (system: let
      pkgs = nixpkgs.legacyPackages.${system};

      python = pkgs.python312;

      pythonDeps = ps:
        with ps; [
          attrs
          bcrypt
          blinker
          click
          colorama
          dnspython
          flasgger
          flask
          flask-cors
          flask-jwt-extended
          itsdangerous
          jinja2
          jsonschema
          jsonschema-specifications
          markupsafe
          mistune
          packaging
          pyjwt
          pymongo
          pyyaml
          referencing
          rpds-py
          six
          typing-extensions
          werkzeug
          python-dotenv
        ];
    in {
      devShells.default = pkgs.mkShell {
        name = "api-citas-flask-dev";

        nativeBuildInputs = with pkgs; [
          python
          python.pkgs.venvShellHook # automatically creates & activates venv
          python.pkgs.pip
        ];

        buildInputs = with pkgs; [
          (python.withPackages pythonDeps)
          python.pkgs.pytest
          python.pkgs.pytest-cov
          python.pkgs.black
          python.pkgs.ruff
          python.pkgs.flask-migrate
          python.pkgs.mongomock
        ];

        # Automatically set up the venv with exact requirements on first entry
        venvDir = "./.venv";

        postVenvCreation = ''
          # Upgrade pip once
          ${python.interpreter} -m pip install --upgrade pip > /dev/null 2>&1 || true

          # Install exact requirements only if the venv is fresh or missing Flask
          if ! pip list --format=freeze | grep -q Flask; then
            echo "Installing exact dependencies from requirements.txt ..."
            pip install -r requirements.txt
          fi
        '';

        shellHook = ''
          # Load the .env file (if supplied)
          # Things of note:
          # As it can be see, FLASK_APP and FLASK_ENV vars will be (over)set here.
          # the python app (application.py) will try to load the .env itself as well
          [ -f .env ] && export $(grep -v '^#' .env | xargs)

          export FLASK_APP=application.py
          export FLASK_ENV=development

          echo ""
          echo "Flask API Citas - Development Environment"
          echo "Python: ${python.version}"
          echo "Entorno virtual: $venvDir"
          echo ""
          echo "Useful commands:"
          echo "  flask run                    -> Start flask server"
          echo "  python ./migrations/001_init_clinica.py -> Populate database"
          echo "  pytest -v                    -> Run tests"
          echo "  black . && ruff check .      -> Format and Lint"
          echo ""
        '';
      };
    });
}
