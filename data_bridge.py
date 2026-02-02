- name: Ejecutar motor Kira
        env:
          FIREBASE_CONFIG: ${{ secrets.FIREBASE_CONFIG }}
        run: python scripts/data_bridge.py
