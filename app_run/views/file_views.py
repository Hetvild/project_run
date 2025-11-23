from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from app_run.services import read_excel_file


class UploadFileAPIView(APIView):
    def post(self, request):
        # Если файл не передан, то возвращаем ошибку 400
        if not request.FILES:
            return Response(
                {"error": "Файл не был загружен"}, status=status.HTTP_400_BAD_REQUEST
            )
        # Получаем переданный файл из запроса
        uploaded_file = request.FILES.get("file", None)

        # Проверяем, что файл не пустой и имеет расширение .xlsx
        if uploaded_file.name.endswith(".xlsx"):
            # Отправляем полученный файл на чтение
            data_error = read_excel_file(uploaded_file)

            return Response(data_error, status=status.HTTP_200_OK)

        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
