'use strict';

/**
 * exhibit service
 */

const { createCoreService } = require('@strapi/strapi').factories;

module.exports = createCoreService('api::exhibit.exhibit');
