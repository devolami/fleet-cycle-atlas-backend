from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import LogbookTrip
from .serializers import LogSerializers
from .config import HOSConfig
from .logbook_generator import LogbookGenerator
from .feasibility import validate_trip_feasibility


class LogEntryViewSet(viewsets.ModelViewSet):
    queryset = LogbookTrip.objects.all()
    serializer_class = LogSerializers
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=["post"])
    def generate_logbook(self, request):
        data = request.data
        required_fields = ["total_distance_miles", "total_driving_time", "current_cycle_hour", "pickup_time"]
        missing = [field for field in required_fields if field not in data]
    
        if missing:
            return Response(
                {"error": f"Missing required fields: {', '.join(missing)}"}, 
                status=status.HTTP_400_BAD_REQUEST
        )
        try:
            # 1. Extract and normalize inputs
            total_dist = float(data.get("total_distance_miles"))
            total_time_mins = float(data.get("total_driving_time"))
            current_cycle_hour = float(data.get("current_cycle_hour"))
            pickup_time = float(data.get("pickup_time"))
            
            config = HOSConfig()
            # 2. FEASIBILITY CHECK
            is_possible, error_msg = validate_trip_feasibility(
                total_dist=total_dist,
                total_time_mins=total_time_mins,
                config=config,
                current_cycle_hour=current_cycle_hour
            )

            if not is_possible:
                return Response({"error": error_msg}, status=400)

            # 3. LOGBOOK GENERATION
            generator = LogbookGenerator(
                total_dist=total_dist,
                total_time_mins=total_time_mins,
                config=config
            )
            logbooks = generator.generate(pickup_time_mins=pickup_time)
            
            return Response(logbooks)

        except (ValueError, TypeError) as e:
            return Response(
                {"error": f"Invalid input format: {str(e)}. Numeric values required."}, 
                status=400
            )