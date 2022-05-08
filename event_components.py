from abc import ABC, abstractmethod


# class BaseDispatchComponent:
#     @classmethod
#     def dispatch(cls, caller, *args, **kwargs):
#         caller(cls.EVENT_TYPE, *args, **kwargs)
#
# # class BaseHandleComponent(ABC):
# #     @abstractmethod
# #     def handle(self):
# #         pass
#
#
# class Join(BaseDispatchComponent):
#     EVENT_TYPE = 'JOIN'
#
#     # @classmethod
#     # def dispatch(cls, *args, **kwargs):
#     #     super().dispatch(*args, **kwargs)
#
#     @classmethod
#     def handle(self):
#         pass
#
#
# class ObjectCreated(BaseDispatchComponent):
#     EVENT_TYPE = 'OBJECT_CREATED'
#
#     @classmethod
#     def handle(self):
#         pass
