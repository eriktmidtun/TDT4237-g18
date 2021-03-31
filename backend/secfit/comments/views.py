from django.shortcuts import render
from rest_framework import generics, mixins
from comments.models import Comment, Like
from rest_framework import permissions
from comments.permissions import IsCommentVisibleToUser, CanUserCommentOnWorkout
from workouts.permissions import IsOwner, IsReadOnly
from comments.serializers import CommentSerializer, LikeSerializer
from django.db.models import Q
from rest_framework.filters import OrderingFilter

# Create your views here.
class CommentList(
    mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView
):
    # queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated & CanUserCommentOnWorkout]
    filter_backends = [OrderingFilter]
    ordering_fields = ["timestamp"]

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        workout_pk = self.kwargs.get("pk")
        qs = Comment.objects.none()

        if workout_pk:
            qs = Comment.objects.filter(workout=workout_pk)
        elif self.request.user:
            """A comment should be visible to the requesting user if any of the following hold:
            - The comment is on a public visibility workout
            - The comment was written by the user
            - The comment is on a coach visibility workout and the user is the workout owner's coach
            - The comment is on a workout owned by the user
            """
            qs = Comment.objects.filter(
                Q(workout__visibility="PU")
                | Q(owner=self.request.user)
                | (
                    Q(workout__visibility="CO")
                    & Q(workout__owner__coach=self.request.user)
                )
                | Q(workout__owner=self.request.user)
            ).distinct()

        return qs


class CommentDetail(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView,
):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [
        permissions.IsAuthenticated & IsCommentVisibleToUser & (IsOwner | IsReadOnly)
    ]

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class LikeList(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    serializer_class = LikeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        return Like.objects.filter(owner=self.request.user)


class LikeDetail(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView,
):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
