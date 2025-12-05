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
          # Carga .env automáticamente. Pyuthon se encarga de cargarlo automáticamente, pero no pasa nada por tener esto duplicado
          [ -f .env ] && export $(grep -v '^#' .env | xargs)

          export FLASK_APP=application.py
          export FLASK_ENV=development

          echo ""
          echo "Flask API Citas - Entorno de desarrollo listo"
          echo "Python: ${python.version}"
          echo "Entorno virtual: $venvDir"
          echo ""
          echo "Comandos útiles:"
          echo "  flask run                    -> iniciar servidor"
          echo "  python ./migrations/001_init_clinica.py -> ejecutar migración"
          echo "  pytest -v                    -> ejecutar tests"
          echo "  black . && ruff check .      -> formatear y lint"
          echo ""
        '';
      };
    });
}
