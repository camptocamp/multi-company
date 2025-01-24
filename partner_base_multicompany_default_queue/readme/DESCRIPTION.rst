Glue module inbetween `partner_base_multicompany` and `queue_job`.

The propagation of the fields can be costly given the amount of fields to be propagated
and the amount of companies.

With this module, we want to make the propagation of the fields asynchronous with the creation of queue_jobs.
