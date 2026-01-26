from rest_framework.response import Response
from rest_framework import viewsets, permissions
from rest_framework.decorators import action

from .models import LogbookTrip
from .config import HOSConfig
from .feasibility import validate_trip_feasibility
from .serializers import LogSerializers
from .logbook_generator import LogbookGenerator

class LogEntryViewSet(viewsets.ModelViewSet):
    queryset = LogbookTrip.objects.all()
    serializer_class = LogSerializers
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=["post"])
    def generate_logbook(self, request):
        data = request.data
        try:
            # 1. Extract and normalize inputs
            total_dist = float(data.get("total_distance_miles", 0))
            total_time_mins = float(data.get("total_driving_time", 0))
            current_cycle_hour = float(data.get("current_cycle_hour", 0))
            pickup_time = float(data.get("pickup_time", 0))
            
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