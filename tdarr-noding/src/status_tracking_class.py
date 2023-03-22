class StatusTracking:
    def __init__(self, status_file):
        if status_file is None:
            self.status_file = None
            self.status_dict={}
        else:
            self.status_dict={}
            self.status_file = status_file
            self.state = status_file["state"]
            self.server_status = status_file["tdarr_server"]["state"]

    def set_server_status(self,server_status):
        self.status_dict["tdarr_server"]={"state": server_status}

# class NodeStatus:
#     def __init__(self, node_status_section):
#         if node_status_section is not None:
#             workers_dictionary = node_status_section["workers"]
#
#             self.read_in_workers(workers_dictionary)
#
#     def read_in_workers(self, workers_dictionary):
#         healthcheck_limits = workers_dictionary["healthcheck_worker_limits"]
#         healthcheck_current = workers_dictionary["healthcheck_worker_current"]
#         transcode_limits = workers_dictionary["transcode_worker_limits"]
#         transcode_current = workers_dictionary["transcode_worker_current"]
#
#         self.Healthcheck = Worker(healthcheck_limits, healthcheck_current)
#         self.Transcode = Worker(transcode_limits, transcode_current)
#
#
# class Worker:
#     def __init__(self, limits, current):
#         self.cpu_limit_min = limits["min_cpu"]
#         self.cpu_limit_max = limits["max_cpu"]
#         self.gpu_limit_min = limits["min_gpu"]
#         self.gpu_limit_max = limits["max_gpu"]
#         self.cpu_current_min = limits["min_cpu"]
#         self.cpu_current_max = limits["max_cpu"]
#         self.gpu_current_min = limits["min_gpu"]
#         self.gpu_current_max = limits["max_gpu"]
#
#         self.cpu_limit_min = current["min_cpu"]
#         self.cpu_limit_max = current["max_cpu"]
#         self.gpu_limit_min = current["min_gpu"]
#         self.gpu_limit_max = current["max_gpu"]
#         self.cpu_current_min = current["min_cpu"]
#         self.cpu_current_max = current["max_cpu"]
#         self.gpu_current_min = current["min_gpu"]
#         self.gpu_current_max = current["max_gpu"]
