import os
import qiskit
from qiskit import IBMQ, Aer
import uuid
import pickle

IBMQ.load_account()

def _prep():
    if 'archive' not in os.listdir():
        os.mkdir('archive')
                    
class Archive():
    '''
    A serializable equivalent to the Qiskit job object.
    '''
    def __init__(self, job, ):
        self.job_id = job.job_id()
        self.backend = job.backend()
        self.metadata = job.metadata
        self.version = job.version
        if 'aer' in self.backend.name():
            self._result = job.result()
        else:
            self._result = None
        
    def result(self):
        if self._result==None:
            backend = get_backend(self.backend.name())
            job = backend.retrieve_job(self.job_id)
            self._result = job.result()
        return self._result
        
            
def get_backend(backend_name):
    '''
    Given a string that specifies a backend, returns the backend object
    '''
    if type(backend_name) is str:
        if 'aer' in backend_name:
            backend = Aer.get_backend(backend_name)
        else:
            providers = IBMQ.providers()
            p = 0
            no_backend = True
            for provider in providers:
                if no_backend:
                    backends = provider.backends()
                    for potential_backend in backends:
                        if potential_backend.name()==backend_name:
                            backend = potential_backend
                            no_backend = False
            if no_backend:
                print('No backend was found matching '+device+' with your providers.')
    else:
        backend = backend_name
    return backend


def submit_job(backend_name, circuits, path='',
               job_name=None, job_share_level=None, job_tags=None, experiment_id=None, header=None,
               shots=None, memory=None, qubit_lo_freq=None, meas_lo_freq=None, schedule_los=None,
               meas_level=None, meas_return=None, memory_slots=None, memory_slot_size=None,
               rep_time=None, rep_delay=None, init_qubits=None, parameter_binds=None, use_measure_esp=None,
               **run_config):
    '''
    Given a backend name and the arguments for the `run` method of the backend object, submits the job
    and returns the archive id.
    '''
    
    # get backend
    backend = get_backend(backend_name)
    backend_name = backend.name() 
    
    # submit job
    job = backend.run(circuits, job_name=None, job_share_level=None, job_tags=None, experiment_id=None, header=None,
                      shots=None, memory=None, qubit_lo_freq=None, meas_lo_freq=None, schedule_los=None,
                      meas_level=None, meas_return=None, memory_slots=None, memory_slot_size=None,
                      rep_time=None, rep_delay=None, init_qubits=None, parameter_binds=None, use_measure_esp=None,
                      **run_config)

    # create archive
    archive = Archive(job)
    if 'job_id' in dir(job):
        archive_id = job.job_id() + '@' + backend_name
    else:
        archive_id = uuid.uuid4().hex + '@' + backend_name
    
    # if an Aer job, get the results
    if 'aer' in job.backend().name():
        archive.result()
       
    # save the archive
    _prep() 
    with open(path + 'archive/'+archive_id, 'wb') as file:
        pickle.dump(Archive(job), file)
        
    # return the id
    return archive_id


def get_job(archive_id):
    '''
    Returns the Qiskit job object corresponding to a given archive_id
    '''
    job_id, backend_name = archive_id.split('@')
    backend = get_backend(backend_name)
    job = backend.retrieve_job(job_id)
    return job


def get_archive(archive_id, path=''):
    '''
    Returns the saved archive object corresponding to a given archive_id
    '''
    with open(path + 'archive/'+archive_id, 'rb') as file:
        archive = pickle.load(file)
    return archive