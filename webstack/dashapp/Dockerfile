FROM python

WORKDIR /usr/src/app

RUN pip install dash && \
  pip install dash-renderer && \
  pip install dash-html-components && \
  pip install dash-core-components && \
  pip install plotly # Plotly graphing

EXPOSE 8050

CMD ["python", "app.py"]
