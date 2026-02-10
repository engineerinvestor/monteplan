# Return Models

Return models generate asset return paths for the simulation. All models implement the `ReturnModel` protocol.

## ReturnModel Protocol

::: monteplan.models.returns.base.ReturnModel

## MultivariateNormalReturns

::: monteplan.models.returns.mvn.MultivariateNormalReturns

## StudentTReturns

::: monteplan.models.returns.mvn.StudentTReturns

## HistoricalBootstrapReturns

::: monteplan.models.returns.bootstrap.HistoricalBootstrapReturns

## RegimeSwitchingReturns

::: monteplan.models.returns.regime_switching.RegimeSwitchingReturns

## Inflation Models

### OUInflationModel

::: monteplan.models.inflation.OUInflationModel

### RegimeSwitchingInflationModel

::: monteplan.models.inflation.RegimeSwitchingInflationModel

## Stress Scenarios

::: monteplan.models.stress.apply_stress_scenarios
