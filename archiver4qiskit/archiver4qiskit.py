import os
import qiskit
from qiskit import IBMQ, Aer
import uuid
import pickle

try:
    IBMQ.load_account()
except:
    print('Unable to load IBMQ account')

def _prep():
    if 'archive' not in os.listdir():
        os.mkdir('archive')     
_prep()
                    
class Archive():
    '''
    A serializable equivalent to the Qiskit job object.
    '''
    def __init__(self, job, path='', note='', circuits=None):
        
        if 'job_id' in dir(job):
            self.archive_id = job.job_id() + '@' + job.backend().name()
        else:
            self.archive_id = uuid.uuid4().hex + '@' + job.backend().name()

        self.path = path
        
        self.note = note
        self._job_id = job.job_id()
        self._backend = job.backend()
        self._backend.properties() # just needs to be called to load
        self._metadata = job.metadata
        self.version = job.version
        if 'circuits' in dir(job):
            self._circuits = job.circuits()
        else:
            self._circuits = circuits
        if 'qobj' in dir(job):
            self._qobj = job.qobj()
        if 'aer' in self.backend().name():
            self._result = job.result()
        else:
            self._result = None
            
        self.save()
            
    def save(self):
        with open(self.path + 'archive/'+self.archive_id, 'wb') as file:
            pickle.dump(self, file)
        
    def job_id(self):
        return self._job_id
    
    def backend(self):
        return self._backend
    
    def metadata(self):
        return self._job_id
    
    def circuits(self):
        return self._circuits
    
    def qobj(self):
        return self._qobj
        
    def result(self):
        if self._result==None:
            backend = get_backend(self.backend().name())
            job = backend.retrieve_job(self.job_id())
            self._result = job.result()
            self.save()
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
                print('No backend was found matching '+backend_name+' with your providers.')
    else:
        backend = backend_name
    return backend


def submit_job(circuits, backend_name, path='', note='',
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
    job = backend.run(circuits, job_name=job_name, job_share_level=job_share_level, job_tags=job_tags,
                      experiment_id=experiment_id, header=header, shots=shots, memory=memory,
                      qubit_lo_freq=qubit_lo_freq, meas_lo_freq=meas_lo_freq, schedule_los=schedule_los,
                      meas_level=meas_level, meas_return=meas_return, memory_slots=memory_slots,
                      memory_slot_size=memory_slot_size, rep_time=rep_time, rep_delay=rep_delay, init_qubits=init_qubits,
                      parameter_binds=parameter_binds, use_measure_esp=use_measure_esp,
                      **run_config)

    # create archive
    archive = Archive(job, note=note, circuits=circuits)
    
    # if an Aer job, get the results
    if 'aer' in job.backend().name():
        archive.result()
        
    # return the id
    return archive.archive_id


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


def jobid2archive(job_id, backend_name):
    
    backend = get_backend(backend_name)
    job = backend.retrieve_job(job_id)
    
    archive = Archive(job)
    archive.result()
    
    return archive.archive_id