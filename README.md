# archiver4qiskit

### Tools to help record data from Qiskit jobs.

Install with

```
pip install git+https://github.com/NCCR-SPIN/archiver4qiskit.git
```

Import the main tools with

```
from qiskitarchiver import submit_job, get_archive
```

To submit a job use

```
archive_id = submit_job(circuits, backend_name)
```

Here `circuits` are the circuits to run and `backend_name` is a string specifying the backend (for example `'ibmq_bogota'` or `'aer_simulator'`). Other than `backend_name`, arguments from this are passed directly on to the relevant [`run()`](https://qiskit.org/documentation/stubs/qiskit.providers.ibmq.IBMQBackend.html#qiskit.providers.ibmq.IBMQBackend.run) function (which means you need to transpile your circuits first). The returned `archive_id` is a string used to retrieve the job from locally saved files.

To retreive an archive object use

```
archive = get_archive(archive_id)
```

This object functions much the same as the Qiskit job object. For example, `archive.result()` provides the results. Once obtained, the results are incorporated into the saved archive.
